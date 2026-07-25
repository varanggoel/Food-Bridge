# FoodBridge India

AI Agent–powered food redistribution platform. LangGraph orchestrates a
multi-node agent workflow (validate → AI evaluation → NGO selection → email
generation → decision) with real conditional branching, using Groq as the LLM
and Gmail SMTP for real email delivery.

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in real values
uvicorn app.main:app --reload --port 8000
```

Fill in `.env`:
- `MONGODB_URI` — from MongoDB Atlas (free tier cluster connection string)
- `GROQ_API_KEY` — from https://console.groq.com
- `EMAIL_USER` / `EMAIL_PASSWORD` — a Gmail address + a 16-character **App
  Password** (requires 2FA enabled on that Google account: Google Account →
  Security → App Passwords)

Visit `http://localhost:8000/graphql` for the GraphQL Playground to test
queries/mutations directly.

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env          # points VITE_GRAPHQL_URL at your backend
npm run dev
```

Visit `http://localhost:5173`.

## Testing With Your Own Email (for the teacher / grader)

1. Go to the **NGOs** page → add an NGO with your own email address as the
   NGO email (e.g. `teacher@gmail.com`) and any city.
2. Go to **Donate Food** → click **Quick Demo Fill** to prefill sample data,
   then enter your own email as the **Restaurant Email**, and set the
   **Pickup Address / City** close to the NGO's city (within 10km) so the
   distance check passes.
3. Submit. The AI Agent will validate, evaluate, pick the NGO you added, and
   send a real email to that NGO's inbox.
4. Check the **Donations** page to see the AI's decision, reasoning, and
   whether the email was actually sent.

## Deployment

- **Frontend** → Vercel (set `VITE_GRAPHQL_URL` to your deployed backend URL
  in Vercel's environment variables)
- **Backend** → Render (set all `.env` variables in Render's dashboard;
  note the free tier spins down after inactivity, so the first request
  after idling can take 30–50 seconds)

## Architecture

```
React (Vercel) → Apollo Client → GraphQL → FastAPI → LangGraph Agent → MongoDB + Gmail SMTP
```

### LangGraph Flow (with real conditional edges)

```
receive_donation → validate_donation
                        │
              ┌─────────┴─────────┐
        invalid / no NGO      valid + NGO(s) in range
              │                   │
          rejection          evaluate_donation (AI)
              │                   │
              │         ┌─────────┴─────────┐
              │      AI rejects          AI accepts
              │         │                   │
              └─────────┘             select_ngo (AI)
                                             │
                                     generate_email (AI)
                                             │
                                      final_decision
```

Validation includes a 10km Haversine distance check between the donation's
geocoded pickup address (via free OpenStreetMap Nominatim) and each NGO's
geocoded location — NGOs beyond 10km are excluded before the AI even sees
the list.
