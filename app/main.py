from fastapi import FastAPI, HTTPException
from datetime import datetime
import uuid
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

# Dummy database
parking_records = {}

@app.post("/entry")
async def entry(plate: str, parkingLot: int):
    ticket_id = str(uuid.uuid4())
    parking_records[ticket_id] = {
        'plate': plate,
        'parking_lot': parkingLot,
        'entry_time': datetime.now()
    }
    return {"ticket_id": ticket_id}

@app.post("/exit")
async def exit(ticketId: str):
    record = parking_records.get(ticketId)
    if not record:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    time_parked = datetime.now() - record['entry_time']
    total_minutes_parked = time_parked.total_seconds() / 60
    quarters_parked = (total_minutes_parked // 15) + (1 if total_minutes_parked % 15 > 0 else 0)
    charge = quarters_parked * 2.5
    
    return {
        'plate': record['plate'],
        'total_parked_time': str(time_parked),
        'parking_lot_id': record['parking_lot'],
        'charge': charge
    }