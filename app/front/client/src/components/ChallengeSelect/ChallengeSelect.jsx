import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import PasswordModal from '../passwordModal/PasswordModal';
import { validateChallengePassword } from '../../services/challengeServices';
import Swal from 'sweetalert2';

const ChallengeSelect = ({ challenges, selectedChallengeId, onSelectChange }) => {
    const navigate = useNavigate();
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    const [selectorChallengeId, setSelectorChallengeId] = useState(null);

    const handleChange = (event) => {
        const selectedChallengeId = event.target.value;
        setSelectorChallengeId(selectedChallengeId);
        setShowPasswordModal(true);
    };

    const handlePasswordSubmit = async (password) => {
        try {
            const response = await validateChallengePassword(selectorChallengeId, password);
            if (response.isValid) {
                onSelectChange(selectorChallengeId);
                navigate(`/home/card/${selectorChallengeId}`);
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Contraseña incorrecta'
                });
            }
        } catch (error) {
            console.error('Error:', error);
        }
        setShowPasswordModal(false);
    };

    return (
        <>
            <select
                value={selectedChallengeId || ''}
                onChange={handleChange} className='container-select'
            >
                <option value="">Seleccionar reto</option>
                {challenges.map(challenge => (
                    <option key={challenge.id} value={challenge.id}>
                        {challenge.name}
                    </option>
                ))}
            </select>
            {showPasswordModal && (
                <PasswordModal
                    onSubmit={handlePasswordSubmit}
                    onClose={() => {
                        setShowPasswordModal(false);
                        setSelectorChallengeId(null);
                    }}
                />
            )}
        </>
    );
};


export default ChallengeSelect;