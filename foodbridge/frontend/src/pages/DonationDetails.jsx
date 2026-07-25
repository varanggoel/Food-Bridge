import { useParams } from "react-router-dom";
import { useQuery, useMutation } from "@apollo/client";
import { GET_DONATION, RESEND_EMAIL } from "../graphql/operations";

export default function DonationDetails() {
  const { id } = useParams();
  const { data, loading, error, refetch } = useQuery(GET_DONATION, { variables: { id } });
  const [resendEmail, { loading: resending }] = useMutation(RESEND_EMAIL);

  if (loading) return <p className="text-center py-10">Loading...</p>;
  if (error) return <p className="text-center py-10 text-red-600">Error: {error.message}</p>;

  const d = data.donation;
  if (!d) return <p className="text-center py-10">Donation not found.</p>;

  const handleResend = async () => {
    await resendEmail({ variables: { id } });
    refetch();
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-6">
      <h1 className="text-2xl font-bold text-brand-700">Donation Details</h1>

      <Section title="Restaurant Information">
        <Row label="Name" value={d.restaurantName} />
        <Row label="Email" value={d.restaurantEmail} />
        <Row label="Phone" value={d.restaurantPhone} />
        <Row label="Food Type" value={d.foodType} />
        <Row label="Quantity" value={`${d.quantity} kg`} />
        <Row label="Pickup Address" value={`${d.pickupAddress}, ${d.city}`} />
        <Row label="Ready Time" value={d.preparationTime} />
        {d.notes && <Row label="Notes" value={d.notes} />}
      </Section>

      <Section title="AI Decision">
        <Row label="Status" value={d.status} />
        <Row label="Selected NGO" value={d.assignedNGO || "—"} />
        <Row label="NGO Email" value={d.ngoEmail || "—"} />
        <Row label="Reason" value={d.aiReason || "—"} />
      </Section>

      {d.emailSubject && (
        <Section title="Generated Email">
          <p className="font-medium text-gray-800 mb-2">Subject: {d.emailSubject}</p>
          <p className="whitespace-pre-wrap text-gray-600 text-sm">{d.emailBody}</p>
        </Section>
      )}

      <Section title="Email Status">
        <Row label="Sent" value={d.emailSent ? "✅ Yes" : "❌ No"} />
        {d.status === "accepted" && (
          <button
            onClick={handleResend}
            disabled={resending}
            className="mt-3 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2 rounded-full text-sm"
          >
            {resending ? "Resending..." : "Resend Email"}
          </button>
        )}
      </Section>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <h2 className="font-semibold text-brand-700 mb-3">{title}</h2>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <p className="text-sm text-gray-700">
      <span className="font-medium text-gray-500">{label}: </span>
      {value}
    </p>
  );
}
