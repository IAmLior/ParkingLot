import pulumi
import pulumi_aws as aws
from pulumi_docker import Image
import base64

# Constants
ECR_REPOSITORY = 'parking-lot-api'
IMAGE_TAG = 'latest'

config = pulumi.Config()
account_id = aws.get_caller_identity().account_id
region = aws.config.region

def upload():
    # Create or get an existing repository
    repo = aws.ecr.Repository(ECR_REPOSITORY, name=ECR_REPOSITORY)

    # Retrieve an authorization token and use it to set up Docker registry credentials
    def get_registry_info(creds):
        decoded = base64.b64decode(creds.authorization_token).decode()
        username, password = decoded.split(':')
        return {
            "server": creds.proxy_endpoint,
            "username": username,
            "password": password
        }

    registry_info = pulumi.Output.all(repo.registry_id).apply(
        lambda args: aws.ecr.get_authorization_token(registry_id=args[0])
    ).apply(get_registry_info)

    # Build and publish the Docker image
    image = Image("parking-lot-api-image",
                  build={
                      "context":"../app",
                      "dockerfile":"../app/Dockerfile"
                },
                image_name=repo.repository_url.apply(lambda url: f"{url}:latest"),
                registry=registry_info)

    # Export the repository URL
    pulumi.export('repository_url', repo.repository_url)
    pulumi.export('image_uri', image.image_name)

    return repo, image