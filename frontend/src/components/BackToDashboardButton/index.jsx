import { Link } from 'react-router-dom';
import './BackToDashboardButton.css';

function BackToDashboardButton({ className = '' }) {
    const classes = ['back-to-dashboard-btn', className].filter(Boolean).join(' ');

    return (
        <Link to="/" className={classes}>
            <span aria-hidden="true">&larr;</span>
            <span>Volver al Dashboard</span>
        </Link>
    );
}

export default BackToDashboardButton;
