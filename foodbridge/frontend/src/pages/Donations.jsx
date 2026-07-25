import { useQuery } from "@apollo/client";
import { Link } from "react-router-dom";
import { GET_DONATIONS } from "../graphql/operations";

const statusColor = {
  accepted: "bg-brand-100 text-brand-700",
  rejected: "bg-red-100 text-red-700",
  processing: "bg-yellow-100 text-yellow-700",
  error: "bg-gray-200 text-gray-700",
};

export default function Donations() {
  const { data, loading, error } = useQuery(GET_DONATIONS, { pollInterval: 5000 });

  if (loading) return <p className="text-center py-10">Loading...</p>;
  if (error) return <p className="text-center py-10 text-red-600">Error: {error.message}</p>;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-brand-700 mb-6">Donations</h1>
      <div className="bg-white rounded-2xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-brand-50 text-brand-700 text-left">
            <tr>
              <th className="px-4 py-3">Restaurant</th>
              <th className="px-4 py-3">NGO</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Date</th>
            </tr>
          </thead>
          <tbody>
            {data?.donations?.map((d) => (
              <tr key={d.id} className="border-t hover:bg-brand-50 cursor-pointer">
                <td className="px-4 py-3">
                  <Link to={`/donations/${d.id}`} className="text-brand-700 font-medium hover:underline">
                    {d.restaurantName}
                  </Link>
                </td>
                <td className="px-4 py-3">{d.assignedNGO || "—"}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor[d.status] || "bg-gray-100"}`}>
                    {d.status}
                  </span>
                </td>
                <td className="px-4 py-3">{d.emailSent ? "✅ Sent" : "—"}</td>
                <td className="px-4 py-3 text-gray-500">{new Date(d.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {data?.donations?.length === 0 && (
          <p className="text-center py-8 text-gray-500">No donations submitted yet.</p>
        )}
      </div>
    </div>
  );
}
