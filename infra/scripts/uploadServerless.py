import pulumi
import json
import pulumi_aws as aws
import pulumi_aws_apigateway as apigateway

# Constants
IMAGE_TAG = 'latest'

config = pulumi.Config()
account_id = aws.get_caller_identity().account_id
region = aws.config.region


# Serverless solution
def upload(repo, image):
    # An execution role to use for the Lambda function
    lambda_role = aws.iam.Role("lambda-role", 
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com",
                },
            }],
        })
    )

    # Attach the necessary policies to the role
    policy_attach = aws.iam.RolePolicyAttachment("lambda-basic-execution",
        role=lambda_role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    )

    ecr_policy = aws.iam.RolePolicy("lambda-ecr-policy",
        role=lambda_role.id,
        policy=pulumi.Output.all(repo.arn).apply(lambda arn: json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage",
                        "ecr:BatchCheckLayerAvailability"
                    ],
                    "Resource": arn
                }
            ]
        }))
    )

    # Create the Lambda function with the correct image URI configuration
    image_uri = repo.repository_url.apply(lambda url: f"{url}:{IMAGE_TAG}")

    function = aws.lambda_.Function('parkingLotApiFunction',
        role=lambda_role.arn,
        package_type='Image',
        image_uri=image_uri,
        timeout=120,
        memory_size=1024,
            environment=aws.lambda_.FunctionEnvironmentArgs(
            variables={
                "ENVIRONMENT": "lambda"
            }
        ),
        opts=pulumi.ResourceOptions(depends_on=[policy_attach, ecr_policy, image])
    )

    api = apigateway.RestAPI("parkingLotApiGateway",
    routes=[
        apigateway.RouteArgs(path="/entry", method=apigateway.Method.POST, event_handler=function),
        apigateway.RouteArgs(path="/exit", method=apigateway.Method.POST, event_handler=function)
    ],
    opts=pulumi.ResourceOptions(depends_on=[function]))

    # Export the endpoint URL
    pulumi.export("url", api.url)