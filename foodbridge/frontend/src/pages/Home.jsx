import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-brand-700 mb-4">FoodBridge India</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          An AI Agent-powered platform connecting restaurants with surplus food
          to nearby NGOs, reducing waste and fighting hunger.
        </p>
        <div className="mt-6 flex justify-center">
          <Link to="/donate" className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-3 rounded-full font-medium shadow">
            Donate Food
          </Link>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-12">
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="font-semibold text-brand-700 mb-2">🌍 SDG 2 — Zero Hunger</h2>
          <p className="text-gray-600 text-sm">
            Redirecting surplus restaurant food to communities in need instead of the landfill.
          </p>
        </div>
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="font-semibold text-brand-700 mb-2">♻️ SDG 12 — Responsible Consumption</h2>
          <p className="text-gray-600 text-sm">
            Promoting responsible production patterns by ensuring surplus food is used, not wasted.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow p-8">
        <h2 className="text-xl font-semibold text-brand-700 mb-4">How It Works</h2>
        <ol className="space-y-3 text-gray-700 list-decimal list-inside">
          <li>A restaurant submits a food donation with pickup details.</li>
          <li>An AI Agent (built with LangGraph) validates the donation and checks NGOs within the same city.</li>
          <li>The AI evaluates suitability, selects the best matching NGO, and drafts a professional email.</li>
          <li>The backend automatically emails the selected NGO with all the details — instantly.</li>
        </ol>
      </div>
    </div>
  );
}
