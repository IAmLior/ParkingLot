**Exercise 1 - Parking Lot**

This is a cloud-based system to manage a parking lot.

**Setting up**
After having pulumi set on your computer and connected to your aws account, just use `pulumi up`

**Endpoints:**
POST /entry?plate=123-123-123&parkingLot=382
Returns ticket id

POST /exit?ticketId=1234
Returns the license plate, total parked time, the parking lot id and the charge (based on 15 minutes increments).

**HTTP Calls examples:**

**Ec2 deployment:**

curl --location --request POST 'http://ec2-54-164-126-200.compute-1.amazonaws.com:8080/entry?plate=3999&parkingLot=1

curl --location --request POST 'http://ec2-3-90-183-106.compute-1.amazonaws.com:8080/exit?ticketId=840f86a0-9fe6-4956-ba3b-d2e5f554dc1a


**Serverless (Lambda function) deployment:**

curl --location --request POST 'https://f59ibsv8ii.execute-api.us-east-1.amazonaws.com/stage/entry?plate=999&parkingLot=1

curl --location --request POST 'https://f59ibsv8ii.execute-api.us-east-1.amazonaws.com/stage/exit?ticketId=62496bfc-e174-4978-9f16-5427cf5af76f
