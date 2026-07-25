import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import DonateFood from "./pages/DonateFood";
import NGOs from "./pages/NGOs";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/donate" element={<DonateFood />} />
        <Route path="/ngos" element={<NGOs />} />
      </Routes>
    </BrowserRouter>
  );
}
