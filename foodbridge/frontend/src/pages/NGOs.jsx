import { useState } from "react";
import { useQuery, useMutation } from "@apollo/client";
import { GET_NGOS, CREATE_NGO, DELETE_NGO } from "../graphql/operations";

export default function NGOs() {
  const { data, loading, refetch } = useQuery(GET_NGOS);
  const [createNGO, { loading: creating }] = useMutation(CREATE_NGO);
  const [deleteNGO] = useMutation(DELETE_NGO);
  const [form, setForm] = useState({ name: "", email: "", city: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createNGO({ variables: { input: form } });
    setForm({ name: "", email: "", city: "" });
    refetch();
  };

  const handleDelete = async (id) => {
    await deleteNGO({ variables: { id } });
    refetch();
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-brand-700 mb-2">NGOs</h1>
      <p className="text-sm text-gray-500 mb-6">
        Add an NGO with your own email to test that the AI-selected notification actually reaches you.
      </p>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow p-6 grid md:grid-cols-3 gap-3 mb-8">
        <input placeholder="Test NGO" required value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="border border-gray-300 rounded-lg px-3 py-2 md:col-span-1" />
        <input placeholder="myemail@gmail.com" required type="email" value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          className="border border-gray-300 rounded-lg px-3 py-2 md:col-span-1" />
        <input placeholder="City" required value={form.city}
          onChange={(e) => setForm({ ...form, city: e.target.value })}
          className="border border-gray-300 rounded-lg px-3 py-2 md:col-span-1" />
        <button disabled={creating} className="md:col-span-3 bg-brand-600 hover:bg-brand-700 text-white rounded-full py-2 font-medium">
          {creating ? "Adding..." : "Add NGO"}
        </button>
      </form>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="space-y-3">
          {data?.ngos?.map((ngo) => (
            <div key={ngo.id} className="bg-white rounded-xl shadow p-4 flex justify-between items-center">
              <div>
                <p className="font-medium text-gray-800">{ngo.name}</p>
                <p className="text-sm text-gray-500">{ngo.email} · {ngo.city}</p>
              </div>
              <button onClick={() => handleDelete(ngo.id)} className="text-red-500 text-sm hover:underline">
                Delete
              </button>
            </div>
          ))}
          {data?.ngos?.length === 0 && <p className="text-gray-500">No NGOs yet. Add one above.</p>}
        </div>
      )}
    </div>
  );
}
