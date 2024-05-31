import pulumi
import pulumi_aws as aws

# Constants
ECR_REPOSITORY = 'parking-lot-api'
IMAGE_TAG = 'latest'

config = pulumi.Config()
account_id = aws.get_caller_identity().account_id
region = aws.config.region

def upload(repo, image):
    # EC2 Solution
    ami = aws.ec2.get_ami(most_recent=True,
                          owners=["137112412989"],
                          filters=[{"name":"name", "values":["amzn2-ami-hvm-*"]}])

    # Create a security group to allow HTTP ingress
    security_group = aws.ec2.SecurityGroup('parkingLotSecurityGroup',
                                           description='Enable HTTP and SSH access',
                                           ingress=[
                                               {'protocol': 'tcp',
                                                'from_port': 8080,
                                                'to_port': 8080,
                                                'cidr_blocks': ['0.0.0.0/0']},
                                               {'protocol': 'tcp',
                                                'from_port': 22,
                                                'to_port': 22,
                                                'cidr_blocks': ['0.0.0.0/0']}
                                           ],
                                           egress=[
                                               {'protocol': '-1',
                                                'from_port': 0,
                                                'to_port': 0,
                                                'cidr_blocks': ['0.0.0.0/0']},
                                           ])

    # IAM Role for EC2 Instance with ECR access
    ec2_role = aws.iam.Role("ec2-instance-role", assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }]
    }""")

    policy_attachment = aws.iam.RolePolicyAttachment("ecr-policy-attachment",
        role=ec2_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly")

    instance_profile = aws.iam.InstanceProfile("instanceProfile", role=ec2_role.name)

    instance_user_data = pulumi.Output.all(account_id, region, image.image_name).apply(
        lambda args: f"""
    #!/bin/bash
    echo ECS_CLUSTER=my-cluster >> /etc/ecs/ecs.config
    yum update -y
    yum install -y amazon-ecs-init
    systemctl enable --now ecs

    # Install Docker
    yum install -y docker
    systemctl start docker
    systemctl enable docker

    # Login to ECR
    aws ecr get-login-password --region {args[1]} | docker login --username AWS --password-stdin {args[0]}.dkr.ecr.{args[1]}.amazonaws.com

    # Run the Docker container from ECR
    docker run -d --restart=always --name parking-lot-api -p 8080:8080 {args[2]}
    """
    )

    instance = aws.ec2.Instance('parkingLotInstance',
                                instance_type='t2.micro',
                                vpc_security_group_ids=[security_group.id],
                                ami=ami.id,
                                iam_instance_profile=instance_profile.name,
                                user_data=instance_user_data)

    # Export the public IP of the instance
    pulumi.export('publicIp', instance.public_ip)
    pulumi.export('publicHostName', instance.public_dns)
