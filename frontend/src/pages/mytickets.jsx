import { useEffect, useState } from "react";
import api from "../services/api";
import "./mytickets.css";

function MyTickets() {
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const token = localStorage.getItem("token");

      const response = await api.get("/tickets/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setTickets(response.data.tickets);
    } catch (error) {
      console.log(error);
      alert("Unable to load tickets");
    }
  };

  return (
    <div className="page-container">
      <h2 className="page-title">📋 My Tickets</h2>

      {tickets.length === 0 ? (
        <p style={{ textAlign: "center" }}>No tickets found.</p>
      ) : (
        <div className="ticket-grid">
          {tickets.map((ticket) => (
            <div className="ticket-card" key={ticket.id}>
              <h3>{ticket.title}</h3>

              <p>{ticket.description}</p>

              <p>
                <strong>Category:</strong>{" "}
                <span className="badge category">
                  {ticket.category}
                </span>
              </p>

              <p>
                <strong>Priority:</strong>{" "}
                <span className="badge priority">
                  {ticket.priority}
                </span>
              </p>

              <p>
                <strong>Status:</strong>{" "}
                <span className="badge status">
                  {ticket.status}
                </span>
              </p>

              <p className="ticket-id">
                <strong>Ticket ID:</strong>
                <br />
                {ticket.id}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyTickets;