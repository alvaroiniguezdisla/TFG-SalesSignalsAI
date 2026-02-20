import React from 'react';
import './Spinner.css';

function Spinner({ message = "Cargando..." }) {
    return (
        <div className="spinner-container">
            <div className="simple-spinner"></div>
            {message && <p className="spinner-text">{message}</p>}
        </div>
    );
}

export default Spinner;
