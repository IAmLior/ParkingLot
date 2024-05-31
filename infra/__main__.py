from scripts import uploadDockerImage, uploadServerless, uploadEc2

repo, image = uploadDockerImage.upload()
uploadServerless.upload(repo, image)
uploadEc2.upload(repo, image)