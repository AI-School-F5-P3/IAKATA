import { useState, useEffect } from 'react';
import { getTargetState, deleteTargetState } from '../../services/targetStateServices';
import update from "../../assets/img/EditButton.svg";
import { useWebSocket } from '../../context/SocketContext';
import { useSocket } from '../../utils/UseSocket';
import './css/SelectAll.css';
import more from '../../assets/img/Plus.svg';
import delte from '../../assets/img/delete.svg';
import MentalContras from './MentalContras';
import Obstacle from '../forms/Obstacle';
import TargetState from '../forms/TargetState';
import ContrastMental from '../forms/CreateContrastMental';
import ObstacleSelect from './ObstacleSelect';
import AddCMLogo from '../../assets/img/CMButton.svg'
import AddObstacleLogo from '../../assets/img/ObstacleButton.svg';
import Swal from 'sweetalert2';

const TargetSta = ({ challengeId }) => {
    const [targetStates, setTargetState] = useState([]);
    const [createTarget, setCreateTarget] = useState(false);
    const [editTargetState, setEditTargetState] = useState(false);
    const [editContrast, setEditContrast] = useState(false);
    const [editObstacle, setEditObstacle] = useState(false);
    const [editTargetId, setEditTargetId] = useState();
    const [loading, setLoading] = useState(false);
    const { WS_EVENTS, sendMessage } = useWebSocket();

    useSocket(
        WS_EVENTS.TARGET_STATE,
        challengeId,
        (payload) => {
            if (Array.isArray(payload)) {
                const filteredStates = payload.filter(
                    state => state.challenge_id === challengeId
                );
                setTargetState(filteredStates);
            } else if (payload.deleted) {
                setTargetState(prev => prev.filter(ts => ts.id !== payload.id));
            } else if (payload.challenge_id === challengeId) {
                setTargetState(prev => {
                    const exists = prev.some(target => target.id === payload.id);
                    if (exists) {
                        return prev.map(target => 
                            target.id === payload.id ? payload : target
                        );
                    }
                    return [...prev, payload];
                });
            }
            setLoading(false);
        }
    );

    useEffect(() => {
        const fetchTargetState = async () => {
            try {
                const targetStateData = await getTargetState(challengeId);
                if (targetStateData) {
                    const filteredStates = targetStateData.filter(
                        state => state.challenge_id === challengeId
                    );
                    setTargetState(filteredStates);
                }
            } catch (error) {
                console.error('Error fetching target states:', error);
            } finally {
                setLoading(false);
            }
        };

        if (challengeId) {
            setLoading(true);
            fetchTargetState();
        }
    }, [challengeId]);
    
    const handleDelete = async (targetStateId) => {
        try {
            const result = await Swal.fire({
                title: '¿Estás seguro?',
                text: "Esta acción no se puede deshacer",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#002661',
                cancelButtonColor: '#ECF0F1',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            });

            if (result.isConfirmed) {
                const response = await deleteTargetState(targetStateId);
                if (response) {
                    sendMessage(WS_EVENTS.TARGET_STATE, {
                        id: targetStateId,
                        deleted: true,
                        timestamp: Date.now()
                    });
                    setLoading(true);
                }
            }
        } catch (error) {
            console.error('Error deleting target state:', error);
            Swal.fire({
                title: 'Error',
                text: 'No se pudo eliminar el estado objetivo',
                icon: 'error'
            });
        }
    };
    
    return (
        <div className='container-challenge'>
            {targetStates && (
                <>
                    <div className='titleAling'>
                        <h3>ESTADO OBJETIVO
                            <button title='Crear un nuevo estado objetivo' className='targetState' onClick={() => setCreateTarget(true)} >
                                <img src={more} className='createTargetState' />
                            </button>
                        </h3>
                    </div>
                    <div className="centered-table">
                        <table className='container-table'>
                            {targetStates.map((targetState) => (
                                <tbody key={targetState.id}>
                                    <tr className="tr-table">
                                        <td className='title-table'>Estado Objetivo ID</td>
                                        <td className='tr-table'>{targetState.id}</td>
                                    </tr>
                                    <tr className="tr-table">
                                        <td className='title-table'>Descripción</td>
                                        <td className='tr-table'>{targetState.description}</td>
                                    </tr>
                                    <tr className="tr-table">
                                        <td className='title-table'>Fecha de Inicio</td>
                                        <td className='tr-table'>{targetState.start_date}</td>
                                    </tr>
                                    <tr className="tr-table">
                                        <td className='title-table'>Fecha de Meta</td>
                                        <td className='tr-table'>{targetState.date_goal}</td>
                                    </tr>
                                    <tr className="tr-table">
                                        <td className='title-table'>Reto ID</td>
                                        <td className='tr-table'>{targetState.challenge_id}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Acciones</td>
                                        <td className='container-button'>
                                            <button title='Editar' className='CardActionButtonContainer' onClick={() => { setEditTargetId(targetState.id), setEditTargetState(true) }} >
                                                <img src={update} alt="update" className='edit' />
                                            </button>
                                            <button title='Añadir CM' className='CardActionButtonContainer' onClick={() => { setEditTargetId(targetState.id), setEditContrast(true) }}>
                                                <img src={AddCMLogo} className='addCM' />
                                            </button>
                                            <button title='Añadir obstáculo' className='CardActionButtonContainer' onClick={() => { setEditTargetId(targetState.id), setEditObstacle(true) }}>
                                                <img src={AddObstacleLogo} className='addObstacle' />
                                            </button>
                                            <button title='Eliminar' className='CardActionButtonContainer' onClick={() => handleDelete(targetState.id)}>
                                                <img src={delte} alt="img-delete" className='delete' />
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            ))}
                        </table>
                    </div>
                </>
            )}
            {editTargetState && (
                <TargetState targetStateId={editTargetId} challengeId={challengeId} setLoading={setLoading} setEditTargetState={setEditTargetState} isEdit={true} />
            )}
            {createTarget && (
                <TargetState challengeId={challengeId} setLoading={setLoading} setEditTargetState={setCreateTarget} isEdit={false} />
            )}
            {editContrast && <ContrastMental isEdit={false} editTargetId={editTargetId} setLoading={setLoading} setEditContrast={setEditContrast} />}
            <MentalContras targetState={targetStates} editTargetId={editTargetId} />
            {editObstacle && (
                <Obstacle editTargetId={editTargetId} setLoading={setLoading} setEditObstacle={setEditObstacle} isEdit={false} />
            )}
            <ObstacleSelect targetState={targetStates} editTargetId={editTargetId} />
        </div>
    );
}

export default TargetSta;