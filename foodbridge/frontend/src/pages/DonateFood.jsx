import { useState } from "react";
import { useMutation } from "@apollo/client";
import { CREATE_DONATION, CREATE_NGO } from "../graphql/operations";

const DEMO_DEFAULTS = {
  restaurantName: "ABC Restaurant",
  restaurantPhone: "9876543210",
  foodType: "Cooked Rice & Vegetable Curry",
  quantity: "15",
  pickupAddress: "Connaught Place",
  city: "New Delhi",
  notes: "Please call on our number to confirm it as soon as possible and collect it.",
};

const EMPTY_FORM = {
  restaurantName: "",
  restaurantEmail: "",
  restaurantPhone: "",
  foodType: "",
  quantity: "",
  preparationTime: "",
  pickupAddress: "",
  city: "",
  notes: "",
};

export default function DonateFood() {
  const [form, setForm] = useState(EMPTY_FORM);
  const [createDonation, { loading }] = useMutation(CREATE_DONATION);
  const [createNGO] = useMutation(CREATE_NGO);
  const [ngoForm, setNgoForm] = useState({ name: "", email: "", city: "" });
  const [ngosCreated, setNgosCreated] = useState([]);
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleNgoChange = (e) => {
    setNgoForm({ ...ngoForm, [e.target.name]: e.target.value });
  };

  const fillDemo = () => {
    const demoValues = { ...form, ...DEMO_DEFAULTS };
    const now = new Date();
    const localDatetime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);
    const slug = demoValues.restaurantName.replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
    const demoRestaurantEmail = `${slug}@demo.example.com`;
    demoValues.restaurantEmail = demoRestaurantEmail;
    demoValues.preparationTime = localDatetime;
    setForm(demoValues);

    const ngoInput = {
      name: "XYZ NGO",
      email: "",
      city: demoValues.city,
    };
    setNgoForm({ name: ngoInput.name, email: "", city: ngoInput.city });

    createNGO({ variables: { input: ngoInput } })
      .then((res) => {
        if (res && res.data && res.data.createNGO) {
          setNgosCreated((prev) => [...prev, res.data.createNGO]);
        }
      })
      .catch(() => {});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    try {
      // ensure restaurantEmail is populated: prefer form, then created NGO email, then generate from name
      let restaurantEmail = form.restaurantEmail;
      if (!restaurantEmail) {
        if (ngosCreated.length > 0 && ngosCreated[0].email) {
          restaurantEmail = ngosCreated[0].email;
        } else if (form.restaurantName) {
          const slug = form.restaurantName.replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
          restaurantEmail = `${slug}@donor.example.com`;
        }
      }

      const inputPayload = { ...form, restaurantEmail, quantity: parseFloat(form.quantity) };

      const { data } = await createDonation({ variables: { input: inputPayload } });
      setResult(data.createDonation);
      if (data.createDonation.success) {
        setForm(EMPTY_FORM);
      }
    } catch (err) {
      setResult({ success: false, message: err.message });
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-brand-700">Donate Food</h1>
        <button onClick={fillDemo} type="button" className="text-sm bg-brand-700 text-white rounded-full px-4 py-2 shadow-sm hover:bg-brand-800">
          Quick Demo Fill
        </button>
      </div>

      <p className="text-sm text-gray-500 mb-6">
        Use the Quick Demo Fill to preload realistic test data for both the restaurant and an NGO in the same city. In real deployment, the NGO would already be present in the database; for testing, the AI agent would send the email to the NGO in the same city so we can verify the flow.
      </p>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow p-6 space-y-4">
        <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-4">
            <Field label="Restaurant Name" name="restaurantName" value={form.restaurantName} onChange={handleChange} required />
            <Field label="Restaurant Phone" name="restaurantPhone" value={form.restaurantPhone} onChange={handleChange} required />
            <Field label="Food Type" name="foodType" value={form.foodType} onChange={handleChange} required />
            <Field label="Serving" name="quantity" type="number" value={form.quantity} onChange={handleChange} required />
            <Field label="Preparation / Ready Time" name="preparationTime" type="datetime-local" value={form.preparationTime} onChange={handleChange} required />
            <Field label="Pickup Address" name="pickupAddress" value={form.pickupAddress} onChange={handleChange} required />
            <Field label="City" name="city" value={form.city} onChange={handleChange} required />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea name="notes" value={form.notes} onChange={handleChange} rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-400" />
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 border border-dashed rounded-lg bg-gray-50 h-full">
              <div className="mb-2">
                <h3 className="text-sm font-medium">NGO</h3>
              </div>
              <p className="mb-3 text-xs text-gray-600">
                Please write your own email to test if the agent is able to send the email.
              </p>
              <div className="space-y-2">
                <input name="name" placeholder="NGO Name" value={ngoForm.name} onChange={handleNgoChange} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
                <input name="email" placeholder="NGO Email" value={ngoForm.email} onChange={handleNgoChange} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
                <input name="city" placeholder="NGO City" value={ngoForm.city} onChange={handleNgoChange} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
                <div className="flex gap-2">
                  <button type="button" onClick={async () => {
                    try {
                      const { data } = await createNGO({ variables: { input: ngoForm } });
                      if (data && data.createNGO) {
                        setNgosCreated([...ngosCreated, data.createNGO]);
                        setNgoForm({ name: "", email: "", city: "" });
                      }
                    } catch (e) {
                      // ignore
                    }
                  }} className="px-3 py-2 bg-brand-600 text-white rounded-full">Add NGO</button>
                </div>
                {ngosCreated.length > 0 && (
                  <div className="text-sm text-green-700 mt-2">Created NGOs: {ngosCreated.map(n=>n.name).join(', ')}</div>
                )}
              </div>
            </div>
          </div>
        </div>

        <button disabled={loading} type="submit"
          className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-medium py-3 rounded-full">
          {loading ? "AI Agent is evaluating..." : "Submit Donation"}
        </button>
      </form>

      {result && (
        <div className={`mt-6 p-4 rounded-xl ${result.success ? "bg-brand-100 text-brand-800" : "bg-red-100 text-red-800"}`}>
          {result.message}
        </div>
      )}
    </div>
  );
}

function Field({ label, name, value, onChange, type = "text", required }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-400"
      />
    </div>
  );
}
