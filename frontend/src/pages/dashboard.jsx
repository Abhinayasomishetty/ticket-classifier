import { Link } from "react-router-dom";
import "./dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard-container">

      <div className="dashboard-header">
        <h1>AI Ticket Classifier</h1>
        <p>Welcome! Choose an option below.</p>
      </div>

      <div className="dashboard-grid">

        <Link to="/create-ticket" className="dashboard-card">
          <h2>📝</h2>
          <h3>Create Ticket</h3>
          <p>Create a new support ticket and let AI classify it.</p>
        </Link>

        <Link to="/my-tickets" className="dashboard-card">
          <h2>📋</h2>
          <h3>My Tickets</h3>
          <p>View all your submitted tickets.</p>
        </Link>

        <Link to="/solution" className="dashboard-card">
          <h2>🔍</h2>
          <h3>Search Solution</h3>
          <p>Get an AI-powered solution from the knowledge base.</p>
        </Link>

      </div>

    </div>
  );
}

export default Dashboard;