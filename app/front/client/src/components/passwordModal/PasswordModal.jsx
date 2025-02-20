import React, { useState } from 'react';
import './PasswordModal.css';

const PasswordModal = ({ onSubmit, onClose }) => {
    const [password, setPassword] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(password);
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h3>Introduzca la contraseña del reto</h3>
                <form onSubmit={handleSubmit}>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Contraseña"
                    />
                    <div className="modal-buttons">
                        <button type="submit">Verificar</button>
                        <button type="button" onClick={onClose}>Cancelar</button>
                    </div>
                </form>
            </div>
        </div>
    );
};


export default PasswordModal;