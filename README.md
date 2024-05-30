Exercise 1 - Parking Lot

The scenario:
Build a cloud-based system to manage a parking lot.
Camera will recognize license plate and ping cloud service
Actions:
Entry (record time, license plate and parking lot)
Exit (return the charge for the time in the parking lot)
Price – 10$ per hour (by 15 minutes)

Endpoints:
You need to implement two HTTP endpoints:
POST /entry?plate=123-123-123&parkingLot=382
Returns ticket id
POST /exit?ticketId=1234
Returns the license plate, total parked time, the parking lot id and the charge (based on 15 minutes increments).
