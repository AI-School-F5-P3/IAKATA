import { useState, useEffect } from 'react';
import { getResult, deleteResult } from '../../services/resultServices';
import './css/SelectAll.css';
import update from "../../assets/img/EditButton.svg";
import delte from '../../assets/img/delete.svg';
import LearningSelect from './LearningSelect';
import Result from '../forms/Result';
import Learning from '../forms/Learning';
import learningLogo from '../../assets/img/learningButton.svg';
import { useWebSocket } from '../../context/SocketContext';
import { useSocket } from '../../utils/UseSocket';
import Swal from 'sweetalert2';

const ResultsSelect = ({ experiment }) => {
    const [results, setResults] = useState([]);
    const [editResult, setEditResult] = useState(false);
    const [editResultId, setEditResultId] = useState();
    const [createLearning, setCreateLearning] = useState(false);
    const [loading, setLoading] = useState(false);
    const { WS_EVENTS } = useWebSocket();

    useSocket(
        WS_EVENTS.RESULT,
        experiment?.id,
        (payload) => {
            if (Array.isArray(payload)) {
                const filteredResults = payload.filter(
                    result => experiment.some(exp => exp.id === result.experiment_id)
                );
                setResults(filteredResults);
            } else if (payload.deleted) {
                setResults(prev => prev.filter(result => result.id !== payload.id));
            } else {
                setResults(prev => {
                    const exists = prev.some(result => result.id === payload.id);
                    if (exists) {
                        return prev.map(result =>
                            result.id === payload.id ? payload : result
                        );
                    }
                    const belongsToResult = experiment.some(exp => exp.id === payload.experiment_id);
                    return belongsToResult ? [...prev, payload] : prev;
                });
            }
        }
    );


    useEffect(() => {
        const fetchResult = async () => {
            try {
                const resultData = await getResult();
                const arrayResultFiltered = resultData.filter(result =>
                    experiment.some(exp => exp.id === result.experiment_id)
                );
                setResults(arrayResultFiltered);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching Results:', error);
            }
        };

        if (experiment?.length > 0) {
            setLoading(true);
            fetchResult();
        }
    }, [experiment]);

    const handleDelete = async (resultId) => {
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
                try {
                    const response = await deleteResult(resultId);
                    if (response && response.status === 200) {
                        setResults(prevResults =>
                            prevResults.filter(result => result.id !== resultId)
                        );
                        sendMessage(WS_EVENTS.RESULT, {
                            message: 'Result deleted',
                            id: resultId,
                            deleted: true,
                            timestamp: Date.now()
                        });

                        await Swal.fire({
                            title: 'Eliminado',
                            text: 'El registro ha sido eliminado correctamente',
                            icon: 'success',
                            customClass: {
                                popup: 'swal-custom-popup',
                                title: 'swal-custom-title',
                                content: 'swal-custom-content',
                                confirmButton: 'swal-custom-confirm'
                            }
                        });
                    }
                } catch (deleteError) {
                    console.error('Error específico en deleteResult:', deleteError);
                    throw deleteError;
                }
            }
        } catch (error) {
            console.error('Error completo:', error);
            Swal.fire({
                title: 'Error',
                text: error.response?.data?.message || 'Error al eliminar el registro',
                icon: 'error',
                customClass: {
                    popup: 'swal-custom-popup',
                    title: 'swal-custom-title',
                    content: 'swal-custom-content',
                    confirmButton: 'swal-custom-confirm'
                }
            });
        }
    }

    return (
        <div className='container-challenge'>
            {results.length > 0 && (
                <>
                    <h3>RESULTADOS</h3>
                    <div className="centered-table">
                        <table className='container-table'>
                            {results.map((result) => (
                                <tbody className='tr-table' key={result.id}>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Resultado ID</td>
                                        <td className='tr-table'>{result.id}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Experimento ID</td>
                                        <td className='tr-table'>{result.experiment_id}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Descripción</td>
                                        <td className='tr-table'>{result.description}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Fecha</td>
                                        <td className='tr-table'>{result.date}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Analisis</td>
                                        <td className='tr-table'>{result.analysis}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Resultados esperados</td>
                                        <td className='tr-table'>{result.expected_results}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Resultados obtenidos</td>
                                        <td className='tr-table'>{result.results_obtained}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Conclusion</td>
                                        <td className='tr-table'>{result.conclusion}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Siguiente paso</td>
                                        <td className='tr-table'>{result.next_step}</td>
                                    </tr>
                                    <tr className='tr-table'>
                                        <td className='title-table'>Acciones</td>
                                        <td className='container-button'>
                                            <button title='Editar' className='CardActionButtonContainer' onClick={() => { setEditResultId(result.id), setEditResult(true) }}>
                                                <img src={update} alt="logo-update" className='edit' />
                                            </button>
                                            <button title='Añadir aprendizaje' className='CardActionButtonContainer' onClick={() => { setEditResultId(result.id), setCreateLearning(true) }}>
                                                <img src={learningLogo} />
                                            </button>
                                            {/* <button title='Eliminar' className='CardActionButtonContainer' onClick={() => {deleteResult(result.id), setLoading(true)}}><img src={delte} alt="delete" className='delete'/></button> */}
                                            <button title='Eliminar' className='CardActionButtonContainer' onClick={() => handleDelete(result.id)}><img src={delte} alt="delete" className='delete' /></button>

                                        </td>
                                    </tr>
                                </tbody>
                            ))}
                        </table>
                    </div>
                </>
            )}
            {editResult && (
                <Result isEdit={true} editResultId={editResultId} setLoading={setLoading} setEditResult={setEditResult} />
            )}
            {createLearning && <Learning isEdit={false} editResultId={editResultId} setLoading={setLoading} setCreateLearning={setCreateLearning} />}
            <LearningSelect result={results} />
        </div>

    );
}


export default ResultsSelect;
