import { Routes, Route } from "react-router-dom";

import Login from "./pages/login";
import Dashboard from "./pages/dashboard";
import CreateTicket from "./pages/createticket";
import MyTickets from "./pages/mytickets";
import Solution from "./pages/solution";
import Register from "./pages/register";
function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/create-ticket" element={<CreateTicket />} />
      <Route path="/my-tickets" element={<MyTickets />} />
      <Route path="/solution" element={<Solution />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  );
}

export default App;