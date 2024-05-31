from scripts import uploadDockerImage, uploadServerless, uploadEc2

repo, image = uploadDockerImage.upload()
uploadServerless.upload(repo, image)
uploadEc2.upload(repo, image)

# import pulumi
# import json
# import pulumi_aws as aws
# from pulumi_docker import Image
# import pulumi_aws_apigateway as apigateway

# import base64

# # Constants
# ECR_REPOSITORY = 'parking-lot-api'
# IMAGE_TAG = 'latest'

# config = pulumi.Config()
# account_id = aws.get_caller_identity().account_id
# region = aws.config.region

# # Create or get an existing repository
# repo = aws.ecr.Repository(ECR_REPOSITORY, name=ECR_REPOSITORY)

# # Retrieve an authorization token and use it to set up Docker registry credentials
# def get_registry_info(creds):
#     decoded = base64.b64decode(creds.authorization_token).decode()
#     username, password = decoded.split(':')
#     return {
#         "server": creds.proxy_endpoint,
#         "username": username,
#         "password": password
#     }

# registry_info = pulumi.Output.all(repo.registry_id).apply(
#     lambda args: aws.ecr.get_authorization_token(registry_id=args[0])
# ).apply(get_registry_info)

# # Build and publish the Docker image
# image = Image("parking-lot-api-image",
#               build={
#                   "context":"../app",
#                   "dockerfile":"../app/Dockerfile"
#               },
#               image_name=repo.repository_url.apply(lambda url: f"{url}:latest"),
#               registry=registry_info)

# # Export the repository URL
# pulumi.export('repository_url', repo.repository_url)
# pulumi.export('image_uri', image.image_name)

# # Serverless solution

# # An execution role to use for the Lambda function
# lambda_role = aws.iam.Role("lambda-role", 
#     assume_role_policy=json.dumps({
#         "Version": "2012-10-17",
#         "Statement": [{
#             "Action": "sts:AssumeRole",
#             "Effect": "Allow",
#             "Principal": {
#                 "Service": "lambda.amazonaws.com",
#             },
#         }],
#     })
# )

# # Attach the necessary policies to the role
# policy_attach = aws.iam.RolePolicyAttachment("lambda-basic-execution",
#     role=lambda_role.name,
#     policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
# )

# ecr_policy = aws.iam.RolePolicy("lambda-ecr-policy",
#     role=lambda_role.id,
#     policy=pulumi.Output.all(repo.arn).apply(lambda arn: json.dumps({
#         "Version": "2012-10-17",
#         "Statement": [
#             {
#                 "Effect": "Allow",
#                 "Action": [
#                     "ecr:GetDownloadUrlForLayer",
#                     "ecr:BatchGetImage",
#                     "ecr:BatchCheckLayerAvailability"
#                 ],
#                 "Resource": arn
#             }
#         ]
#     }))
# )

# # Create the Lambda function with the correct image URI configuration
# image_uri = repo.repository_url.apply(lambda url: f"{url}:{IMAGE_TAG}")

# function = aws.lambda_.Function('parkingLotApiFunction',
#     role=lambda_role.arn,
#     package_type='Image',
#     image_uri=image_uri,
#     timeout=120,
#     memory_size=1024,
#         environment=aws.lambda_.FunctionEnvironmentArgs(
#         variables={
#             "ENVIRONMENT": "lambda"
#         }
#     ),
#     opts=pulumi.ResourceOptions(depends_on=[policy_attach, ecr_policy])
# )

# api = apigateway.RestAPI("parkingLotApiGateway",
#   routes=[
#     apigateway.RouteArgs(path="/entry", method=apigateway.Method.POST, event_handler=function),
#     apigateway.RouteArgs(path="/exit", method=apigateway.Method.POST, event_handler=function)
#   ],
#   opts=pulumi.ResourceOptions(depends_on=[function]))

# # Export the endpoint URL
# pulumi.export("url", api.url)

# # EC2 Solution
# ami = aws.ec2.get_ami(most_recent=True,
#                       owners=["137112412989"],
#                       filters=[{"name":"name", "values":["amzn2-ami-hvm-*"]}])

# # Create a security group to allow HTTP ingress
# security_group = aws.ec2.SecurityGroup('parkingLotSecurityGroup',
#                                        description='Enable HTTP and SSH access',
#                                        ingress=[
#                                            {'protocol': 'tcp',
#                                             'from_port': 8080,
#                                             'to_port': 8080,
#                                             'cidr_blocks': ['0.0.0.0/0']},
#                                            {'protocol': 'tcp',
#                                             'from_port': 22,
#                                             'to_port': 22,
#                                             'cidr_blocks': ['0.0.0.0/0']}
#                                        ],
#                                        egress=[
#                                            {'protocol': '-1',
#                                             'from_port': 0,
#                                             'to_port': 0,
#                                             'cidr_blocks': ['0.0.0.0/0']},
#                                        ])

# # IAM Role for EC2 Instance with ECR access
# ec2_role = aws.iam.Role("ec2-instance-role", assume_role_policy="""{
#     "Version": "2012-10-17",
#     "Statement": [{
#         "Action": "sts:AssumeRole",
#         "Principal": {
#             "Service": "ec2.amazonaws.com"
#         },
#         "Effect": "Allow",
#         "Sid": ""
#     }]
# }""")

# policy_attachment = aws.iam.RolePolicyAttachment("ecr-policy-attachment",
#     role=ec2_role.name,
#     policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly")

# instance_profile = aws.iam.InstanceProfile("instanceProfile", role=ec2_role.name)

# instance_user_data = pulumi.Output.all(account_id, region, image.image_name).apply(
#     lambda args: f"""
# #!/bin/bash
# echo ECS_CLUSTER=my-cluster >> /etc/ecs/ecs.config
# yum update -y
# yum install -y amazon-ecs-init
# systemctl enable --now ecs

# # Install Docker
# yum install -y docker
# systemctl start docker
# systemctl enable docker

# # Login to ECR
# aws ecr get-login-password --region {args[1]} | docker login --username AWS --password-stdin {args[0]}.dkr.ecr.{args[1]}.amazonaws.com

# # Run the Docker container from ECR
# docker run -d --restart=always --name parking-lot-api -p 8080:8080 {args[2]}
# """
# )

# instance = aws.ec2.Instance('parkingLotInstance',
#                             instance_type='t2.micro',
#                             vpc_security_group_ids=[security_group.id],
#                             ami=ami.id,
#                             iam_instance_profile=instance_profile.name,
#                             user_data=instance_user_data,
#                             opts=pulumi.ResourceOptions(depends_on=[image]))

# # Export the public IP of the instance
# pulumi.export('publicIp', instance.public_ip)
# pulumi.export('publicHostName', instance.public_dns)
