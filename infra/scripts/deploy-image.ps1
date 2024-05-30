# Variables
$REPOSITORY_NAME = "parking-lot-api"
$AWS_REGION = "us-east-1"
$IMAGE_TAG = "latest"
$AWS_ACCOUNT_ID = "654654312742"

# Define Dockerfile directory path relative to the script's location
$DOCKERFILE_DIR = "../app"

# Create the ECR repository if it does not exist
$repoExists = aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $AWS_REGION 2>$null
if ($LASTEXITCODE -ne 0) {
    aws ecr create-repository --repository-name $REPOSITORY_NAME --region $AWS_REGION
}

# Retrieve an authentication token and authenticate your Docker client to your registry
$loginPassword = aws ecr get-login-password --region $AWS_REGION
echo $loginPassword | docker login --username AWS --password-stdin "$($AWS_ACCOUNT_ID).dkr.ecr.$($AWS_REGION).amazonaws.com"

# Build your Docker image using the Dockerfile in the app directory
docker build -t $REPOSITORY_NAME -f "$($DOCKERFILE_DIR)/Dockerfile" $DOCKERFILE_DIR

# Tag your image to match the repository in ECR
docker tag "$($REPOSITORY_NAME):latest" "$($AWS_ACCOUNT_ID).dkr.ecr.$($AWS_REGION).amazonaws.com/$($REPOSITORY_NAME):$($IMAGE_TAG)"

# Push this image to your newly created AWS repository
docker push "$($AWS_ACCOUNT_ID).dkr.ecr.$($AWS_REGION).amazonaws.com/$($REPOSITORY_NAME):$($IMAGE_TAG)"