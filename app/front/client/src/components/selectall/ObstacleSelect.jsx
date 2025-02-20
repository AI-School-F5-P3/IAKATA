import { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { deleteObstacle, getObstacle } from '../../services/obstacleServices';
import update from "../../assets/img/EditButton.svg";
import HypothesisSelect from './HypothesisSelect';
import Obstacle from '../forms/Obstacle';
import delte from '../../assets/img/delete.svg';
import Hypothesis from '../forms/Hypothesis';
import './css/SelectAll.css';
import HypothesisLogo from '../../assets/img/hypothesisButton.svg';
import { useWebSocket } from '../../context/SocketContext';
import { useSocket } from '../../utils/UseSocket';
import Swal from 'sweetalert2';

const ObstacleSelect = ({ targetState, editTargetId }) => {
    const [obstacles, setObstacles] = useState([]);
    const [imgZoom, setImgZoom] = useState(false);
    const [selectedImage, setSelectedImage] = useState(null);
    const [editObstacle, setEditObstacle] = useState(false);
    const [loading, setLoading] = useState(false);
    const [editHypothesis, setEditHypothesis] = useState(false);
    const [editObstacleId, setEditObstacleId] = useState();
    const { WS_EVENTS, sendMessage } = useWebSocket();

    useSocket(WS_EVENTS.OBSTACLE, editTargetId, (payload) => {
        if (!payload) return;

        if (Array.isArray(payload)) {
            if (payload.length === 0) return;
            
            const filteredObstacles = payload.filter(obstacle =>
                obstacle && 
                obstacle.target_state_id &&
                targetState.some(ts => ts.id === obstacle.target_state_id)
            );
            
            if (filteredObstacles.length > 0) {
                setObstacles(filteredObstacles);
            }
        } else {
            setObstacles(prev => {
                if (payload.deleted) {
                    return prev.filter(obs => obs.id !== payload.id);
                }

                const exists = prev.some(obs => obs.id === payload.id);
                const belongsToTarget = targetState.some(ts => 
                    ts.id === payload.target_state_id
                );

                if (!belongsToTarget) return prev;
                
                if (exists) {
                    return prev.map(obs => 
                        obs.id === payload.id ? payload : obs
                    );
                }

                return [...prev, payload];
            });
        }
    });

    useEffect(() => {
        const fetchObstacles = async () => {
            try {
                setLoading(true);
                const obstacleData = await getObstacle();
                const filteredObstacles = obstacleData.filter(obstacle =>
                    targetState.some(ts => ts.id === obstacle.target_state_id)
                );
                setObstacles(filteredObstacles);
            } catch (error) {
                console.error('Error fetching obstacles:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los obstáculos'
                });
            } finally {
                setLoading(false);
            }
        };

        fetchObstacles();
    }, [targetState]);

    const handleClick = (image) => {
        setSelectedImage(image);
        setImgZoom(true);
        window.open(image, '_blank');
    };

    const handleEditClick = (obstacleId) => {
        if (!obstacleId) return;
        setEditObstacleId(obstacleId);
        setEditObstacle(true);
    };

    const handleHypothesisClick = (obstacleId) => {
        if (!obstacleId) return;
        setEditObstacleId(obstacleId);
        setEditHypothesis(true);
    };

    const handleCloseModal = useCallback(() => {
        setEditObstacleId(null);
        setEditObstacle(false);
    }, []);

    const handleDelete = async (obstacleId) => {
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
                const response = await deleteObstacle(obstacleId);

                if (response) {
                    sendMessage(WS_EVENTS.OBSTACLE, {
                        id: obstacleId,
                        deleted: true,
                        timestamp: Date.now()
                    });

                    setObstacles(prev => prev.filter(obs => obs.id !== obstacleId));
                }
            }
        } catch (error) {
            console.error('Error deleting obstacle:', error);
            let errorMessage = error.response?.data?.message || 'No se pudo eliminar el obstáculo';
            Swal.fire({
                title: 'Error',
                text: errorMessage,
                icon: 'error',
                confirmButtonColor: '#002661',
                background: '#ECF0F1',
                customClass: {
                    popup: 'swal-custom-popup',
                    title: 'swal-custom-title',
                    content: 'swal-custom-content',
                    confirmButton: 'swal-custom-confirm'
                }
            });
        }
    };

    return (
        <div className='container-challenge'>
            {obstacles.length > 0 && (
                <>
                    <h3>OBSTACULOS</h3>
                    <div className="centered-table">
                        <table className='container-table'>
                            {obstacles.map((obstacle) => (
                                <tbody key={obstacle.id}>
                                    <tr className="tr-table">
                                        <td className='title-table'>Obstaculo ID</td>
                                        <td className='tr-table'>{obstacle.id}</td>
                                    </tr>
                                    <tr className="tr-table">
                                        <td className='title-table'>EOID</td>
                                        <td className='tr-table'>{obstacle.target_state_id}</td>
                                    </tr>
                                    <tr className="tr-table">
                                        <td className='title-table'>Descripción</td>
                                        <td className='tr-table'>{obstacle.description}</td>
                                    </tr>
                                    <tr className="tr-table">
                                        <td className='title-table'>Imagen</td>
                                        <td className="tr-table">
                                            <img
                                                className='img-form'
                                                src={obstacle.image}
                                                alt="img-form"
                                                onClick={() => handleClick(obstacle.image)}
                                            />
                                        </td>
                                    </tr>
                                    <tr className="tr-table">
                                        <td className='title-table'>Acciones</td>
                                        <td className='container-button'>
                                        <button 
                            title='Editar'
                            className='CardActionButtonContainer'
                            onClick={() => handleEditClick(obstacle.id)}
                        >
                            <img src={update} alt="logo-update" className='logo-edit' />
                        </button>
                        <button 
                            title='Añadir hipotesis' 
                            className='CardActionButtonContainer' 
                            onClick={() => handleHypothesisClick(obstacle.id)}
                        >
                            <img src={HypothesisLogo} alt="hypothesis-logo" />
                        </button>
                        <button
                            title='Eliminar'
                            className='CardActionButtonContainer'
                            onClick={() => handleDelete(obstacle.id)}
                        >
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
            {editObstacle && (
                <Obstacle 
                    isEdit={true}
                    editTargetId={editTargetId}
                    setLoading={setLoading}
                    setEditObstacle={handleCloseModal}
                    editObstacleId={editObstacleId}
                />
            )}
            {editHypothesis && <Hypothesis isEdit={false} editObstacleId={editObstacleId} setLoading={setLoading} setEditHypothesis={setEditHypothesis} />}
            <HypothesisSelect obstacle={obstacles} />
        </div>
    );
};
ObstacleSelect.propTypes = {
    targetState: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
    })).isRequired,
    editObstacleId: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number
    ]),
    editTargetId: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number
    ]),
    setLoading: PropTypes.func.isRequired,
    setEditObstacle: PropTypes.func.isRequired,
    isEdit: PropTypes.bool
};

export default ObstacleSelect;