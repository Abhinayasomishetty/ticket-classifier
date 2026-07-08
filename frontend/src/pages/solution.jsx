import { useState } from "react";
import api from "../services/api";
import "./solution.css";

function Solution() {
  const [ticketId, setTicketId] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!ticketId) {
      alert("Please enter Ticket ID");
      return;
    }

    setLoading(true);
    setAnswer("");

    try {
      const token = localStorage.getItem("token");

      const response = await api.post(
        `/tickets/${ticketId}/search-knowledge`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setAnswer(response.data.answer);
    } catch (error) {
      console.log(error.response?.data);
      alert("Unable to fetch solution");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="solution-card">
        <h2>🔍 Search AI Solution</h2>

        <input
          placeholder="Enter Ticket ID"
          value={ticketId}
          onChange={(e) => setTicketId(e.target.value)}
        />

        <button onClick={handleSearch} disabled={loading}>
          {loading ? "Searching Knowledge Base..." : "Get Solution"}
        </button>

        {loading && (
          <p className="loading">
             AI is searching the knowledge base...
          </p>
        )}

        {answer && (
          <div className="answer-box">
            <h3> AI Suggested Solution</h3>

            <div className="answer-text">
              {answer}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Solution;