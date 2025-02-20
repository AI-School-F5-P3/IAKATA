import { useState, useEffect } from 'react';
import { getLearning, deleteLearning } from '../../services/learningsServices';
import './css/SelectAll.css';
import update from "../../assets/img/EditButton.svg";
import delte from '../../assets/img/delete.svg';
import Learning from '../forms/Learning';
import { useWebSocket } from '../../context/SocketContext';
import { useSocket } from '../../utils/UseSocket';
import Swal from 'sweetalert2';

const LearningSelect = ({ result }) => {
    const [learnings, setLearnings] = useState([]);
    const [editLearning, setEditLearning] = useState(false);
    const [editLearningId, setEditLearningId] = useState();
    const [loading, setLoading] = useState(false);
    const { WS_EVENTS, sendMessage } = useWebSocket();
    
    useSocket(
        WS_EVENTS.LEARNING,
        null,
        (payload) => {
            console.log('mensaje recibido websockets',payload);
            if (Array.isArray(payload)) {
                const filteredLearnings = payload.filter(learning =>
                    result.some(res => res.id === learning.results_id)
                );
                setLearnings(filteredLearnings);
            } else if (payload.deleted) {    
                setLearnings(prev => prev.filter(learning => learning.id !== payload.id));
            } else {
                setLearnings(prev => {
                    const exists = prev.some(learning => learning.id === payload.id);
                    if (exists) {
                        return prev.map(learning =>
                            learning.id === payload.id ? payload : learning
                        );
                    }
                    const belongsToResult = result.some(res => res.id === payload.results_id);
                    return belongsToResult ? [...prev, payload] : prev;
                });
            }
        }
    );

    useEffect(() => {
        const fetchLearnings = async () => {
            try {
                const arrayLearningId = result.map(item => item.id);
                const learningData = await getLearning();

                const arrayLearningFiltered = learningData.filter(learning =>
                    arrayLearningId.includes(learning.results_id)
                );

                setLearnings(arrayLearningFiltered);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching Learnings:', error);
            }
        };

        fetchLearnings();
    }, [result, loading]);

    const handleDelete = async (learningId) => {
        console.log('Deleting learning:', learningId);
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
                    await deleteLearning(learningId);
                    setLearnings(prevLearnings => 
                        prevLearnings.filter(learning => learning.id !== learningId)
                    );
                    console.log("Enviando mensaje de eliminación:", {
                        message: 'Learning deleted',
                        id: learningId,
                        deleted: true,
                        timestamp: Date.now()
                    });
                    sendMessage(WS_EVENTS.LEARNING, {
                        message: 'Learning deleted',
                        id: learningId,
                        deleted: true,
                        timestamp: Date.now()
                    });
            }
        } catch (error) {
            Swal.fire({
                title: 'Error',
                text: error.response?.data?.message || 'No se pudo eliminar el aprendizaje',
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
    
    return (
        <div className='container-challenge' >
            {learnings.length > 0 && (
                <>
                    <h3>APRENDIZAJES</h3>
                    <div className="centered-table">
                        <table className='container-table'>
                            {learnings.map((learning) => (
                                <tbody className='tr-table' key={learning.id}>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Aprendizaje ID</td>
                                        <td className='tr-table'>{learning.id}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Resultados ID</td>
                                        <td className='tr-table'>{learning.results_id}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Descripción</td>
                                        <td className='tr-table'>{learning.description}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Fecha de aprendizaje</td>
                                        <td className='tr-table'>{learning.learning_date}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Acciones</td>
                                        <td className='container-button'>
                                            <button title='Editar' className='CardActionButtonContainer' onClick={() => { setEditLearningId(learning.id), setEditLearning(true) }}>
                                                <img src={update} alt="logo-update" className='edit' />
                                            </button>
                                            <button title='Eliminar' className='CardActionButtonContainer' onClick={() => handleDelete(learning.id)}><img src={delte} alt="delete" className='delete' /></button>
                                        </td>
                                    </tr>
                                </tbody>
                            ))}
                        </table>
                    </div>
                </>
            )}
            {editLearning && (
                <Learning isEdit={true} editLearningId={editLearningId} setLoading={setLoading} setEditLearning={setEditLearning} />
            )}
        </div>
    );
}


export default LearningSelect;