import { useState, useEffect } from 'react';
import { getChallenge, deleteChallenge } from "../../services/challengeServices";
import './css/SelectAll.css';
import update from "../../assets/img/EditButton.svg";
import Challenge from '../forms/Challenge';
import delte from '../../assets/img/delete.svg';
import { useWebSocket } from '../../context/SocketContext';
import { useSocket } from '../../utils/UseSocket';
import Swal from 'sweetalert2';

const SelectAllChallenges = ({ challengeId }) => {
    const [challenges, setChallenges] = useState([]);
    const [editable, setEditable] = useState(false);
    const [loading, setLoading] = useState(false);
    const { socket } = useWebSocket();
    const [actualState, setActualState] = useState({});
    const { WS_EVENTS } = useWebSocket();

    useSocket(
        WS_EVENTS.CHALLENGE,
        null,
        (payload) => {
            if (Array.isArray(payload)) {
                setChallenges(payload.filter(challenge =>
                    challenge.id && !challenge.password
                ));
            } else if (payload.deleted) {
                setChallenges(prev => prev.filter(challenge => challenge.id !== payload.id));
            } else if (payload.updatedChallenge) {
                setChallenges(prev => prev.map(challenge =>
                    challenge.id === payload.updatedChallenge.id
                        ? payload.updatedChallenge
                        : challenge
                ));
            } else {
                setChallenges(prev => {
                    const exists = prev.some(challenge => challenge.id === payload.id);
                    if (exists) {
                        return prev.map(challenge =>
                            challenge.id === payload.id ? payload : challenge
                        );
                    }
                    return [...prev, payload];
                });
            }
        }
    );

    useEffect(() => {
        const fetchChallenges = async () => {
            try {
                const challengesData = await getChallenge();
                setChallenges(challengesData);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching Challenges:', error);
            }
        };

        fetchChallenges();
    }, [challengeId, loading]);

    useEffect(() => {
        if (!socket) return;

        const messageHandler = (event) => {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'CHALLENGE_EVENT':
                    if (data.payload.id === challengeId) {
                        setChallenges(prev => prev.map(challenge => challenge.id === data.payload.id ? { ...challenge, ...data.payload } : challenge));
                    }
                    break;

                case 'ACTUAL_STATE_EVENT':
                    if (data.payload.challenge_id === challengeId) {
                        setActualState(prev => ({ ...prev, ...data.payload }));
                    }
                    break;
            }
        };

        socket.addEventListener('message', messageHandler);
        return () => socket.removeEventListener('message', messageHandler);
    }, [socket, challengeId]);

    const handleDelete = async (challengeId) => {
        try {
            const result = await Swal.fire({
                title: '¿Estás seguro?',
                text: "Esta acción no se puede deshacer",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#002661',
                cancelButtonColor: '#ECF0F1',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar',
                background: '#ECF0F1',
                customClass: {
                    popup: 'swal-custom-popup',
                    title: 'swal-custom-title',
                    content: 'swal-custom-content',
                    confirmButton: 'swal-custom-confirm',
                    cancelButton: 'swal-custom-cancel'
                }
            });

            if (result.isConfirmed) {
                const response = await deleteChallenge(challengeId);
                if (response.status === 200) {
                    setChallenges(prevChallenges =>
                        prevChallenges.filter(challenge => challenge.id !== challengeId)
                    );
                    sendMessage(WS_EVENTS.CHALLENGE, {
                        message: 'Challenge deleted',
                        id: challengeId,
                        deleted: true,
                        timestamp: Date.now()
                    });
                    await Swal.fire({
                        title: 'Eliminado',
                        text: 'El reto ha sido eliminado correctamente',
                        icon: 'success',
                        customClass: {
                            popup: 'swal-custom-popup',
                            title: 'swal-custom-title',
                            content: 'swal-custom-content',
                            confirmButton: 'swal-custom-confirm'
                        }
                    });
                }
            }
        } catch (error) {
            Swal.fire({
                title: 'Error',
                text: error.response?.data?.message || 'No se ha podido eliminar el reto',
                icon: 'error',
                customClass: {
                    popup: 'swal-custom-popup',
                    title: 'swal-custom-title',
                    content: 'swal-custom-content',
                    confirmButton: 'swal-custom-confirm'
                }
            });
        }
    };

    const selectedChallenge = challenges.find(challenge => challenge.id === challengeId);

    return (
        <div className='container-challenge'>
            {selectedChallenge && (
                <>
                    <h3>RETOS</h3>
                    <div className="centered-table">
                        <table className='container-table'>
                            <tbody>
                                <tr className='"tr-table"'>
                                    <td className='title-table'>RetoID:</td>
                                    <td className='tr-table'>{selectedChallenge?.id}</td>
                                </tr>
                                <tr className="tr-table">
                                    <td className='title-table'>Nombre:</td>
                                    <td className='tr-table'>{selectedChallenge?.name}</td>
                                </tr>
                                <tr className="tr-table">
                                    <td className='title-table'>Descripción:</td>
                                    <td className='tr-table'>{selectedChallenge?.description}</td>
                                </tr>
                                <tr className="tr-table">
                                    <td className='title-table'>Fecha Inicio:</td>
                                    <td className='tr-table'>{selectedChallenge?.start_date}</td>
                                </tr>
                                <tr className="tr-table">
                                    <td className='title-table'>Fecha Fin:</td>
                                    <td className='tr-table'>{selectedChallenge?.end_date}</td>
                                </tr>
                                <tr className="tr-table">
                                    <td className='title-table'>Tribe ID:</td>
                                    <td className='tr-table'>{selectedChallenge?.tribe_id}</td>
                                </tr>
                                <tr className="tr-table">
                                    <td className='title-table'>Acciones</td>
                                    <td className='tr-table'>
                                        <button title='Editar' className='CardActionButtonContainer' onClick={() => setEditable(true)}>
                                            <img src={update} alt="logo-update" className='logo-edit' />
                                        </button>
                                        {/* <button title='Eliminar' className='CardActionButtonContainer' onClick={() => {deleteChallenge(selectedChallenge?.id), setLoading(true)}}> */}
                                        <button title='Eliminar' className='CardActionButtonContainer' onClick={() => { handleDelete(selectedChallenge?.id) }}>
                                            <img src={delte} alt="img-delete" className='delete' />
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </>
            )}
            {editable && (
                <Challenge isEdit={true} challengeId={selectedChallenge?.id} setLoading={setLoading} setEditable={setEditable} />
            )}
        </div>
    );
};

export default SelectAllChallenges;