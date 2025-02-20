import { useState, useEffect } from 'react';
import { getTask, deleteTask } from '../../services/taskServices';
import './css/SelectAll.css';
import update from "../../assets/img/EditButton.svg";
import delte from '../../assets/img/delete.svg';
import Task from '../forms/Task';
import { useWebSocket } from '../../context/SocketContext';
import { useSocket } from '../../utils/UseSocket';
import Swal from 'sweetalert2';

const TaskSelect = ({ experiment }) => {
    const [tasks, setTask] = useState([]);
    const [editTask, setEditTask] = useState(false);
    const [editTaskId, setEditTaskId] = useState();
    const [loading, setLoading] = useState(false);
    const { WS_EVENTS } = useWebSocket();

    useSocket(
        WS_EVENTS.TASK,
        experiment?.id,
        (payload) => {
            if (Array.isArray(payload)) {
                const filteredTasks = payload.filter(
                    task => experiment.some(exp => exp.id === task.experiment_id)
                );
                setTask(filteredTasks);
            } else if (payload.deleted) {
                setTask(prev => prev.filter(task => task.id !== payload.id));
            } else {
                setTask(prev => {
                    const exists = prev.some(task => task.id === payload.id);
                    if (exists) {
                        return prev.map(task =>
                            task.id === payload.id ? payload : task
                        );
                    }
                    const belongsToTask = experiment.some(exp => exp.id === payload.experiment_id);
                    return belongsToTask ? [...prev, payload] : prev;
                });
            }
        }
    );

    useEffect(() => {
        const fetchTask = async () => {
            try {
                const taskData = await getTask();
                const arrayTaskFiltered = taskData.filter(task =>
                    experiment.some(exp => exp.id === task.experiment_id)
                );
                setTask(arrayTaskFiltered);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching Tasks:', error);
            }
        };

        if (experiment?.length > 0) {
            setLoading(true);
            fetchTask();
        }
    }, [experiment]);

    const handleDelete = async (taskId) => {
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
                const response = await deleteTask(taskId);
                if (response.status === 200) {
                    setResults(prevTasks =>
                        prevTasks.filter(task => task.id !== taskId)
                    );
                    sendMessage(WS_EVENTS.TASK, {
                        message: 'Task deleted',
                        id: taskId,
                        deleted: true,
                        timestamp: Date.now()
                    });

                    await Swal.fire({
                    title: 'Eliminado',
                    text: 'La tarea ha sido eliminada correctamente',
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
        console.error('Error en deleteTask:', error);
        Swal.fire({
            title: 'Error',
            text: 'No se pudo eliminar la tarea',
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
    <div className='container-challenge' style={{ width: '100%' }}>
        {tasks.length > 0 && (
            <>
                <h3>TAREAS</h3>
                <div className="centered-table">
                    <table className='container-table'>
                        {tasks.map((task) => (
                            <tbody key={task.id}>
                                <tr className='tr-table'>
                                    <td className='title-table'>Tarea ID</td>
                                    <td className='tr-table'>{task.id}</td>
                                </tr>
                                <tr className='tr-table'>
                                    <td className='title-table'>Experimento ID</td>
                                    <td className='tr-table'>{task.experiment_id}</td>
                                </tr>
                                <tr className='tr-table'>
                                    <td className='title-table'>Descripción</td>
                                    <td className='tr-table'>{task.description}</td>
                                </tr>
                                <tr className='tr-table'>
                                    <td className='title-table'>Responsable</td>
                                    <td className='tr-table'>{task.responsible}</td>
                                </tr>
                                <tr className='tr-table'>
                                    <td className='title-table'>Fecha de inicio</td>
                                    <td className='tr-table'>{task.start_date}</td>
                                </tr>
                                <tr className='tr-table'>
                                    <td className='title-table'>Fecha final prevista</td>
                                    <td className='tr-table'>{task.end_date_prev}</td>
                                </tr>
                                <tr className='tr-table'>
                                    <td className='title-table'>Fecha final real</td>
                                    <td className='tr-table'>{task.end_date_real}</td>
                                </tr>
                                <tr className='tr-table'>
                                    <td className='title-table'>Estado</td>
                                    <td className='tr-table'>{task.state}</td>
                                </tr>
                                <tr className='tr-table'>
                                    <td className='title-table'>Acciones</td>
                                    <td className='container-button'>
                                        <button title='Editar' className='CardActionButtonContainer' onClick={() => { setEditTaskId(task.id), setEditTask(true) }} >
                                            <img src={update} alt="logo-update" className='edit' />
                                        </button>
                                        {/* <button title='Eliminar' className='CardActionButtonContainer' onClick={() => { deleteTask(task.id), setLoading(true) }}><img src={delte} alt="img-delete" className='delete' /></button> */}
                                        <button title='Eliminar' className='CardActionButtonContainer' onClick={() => handleDelete(task.id)}><img src={delte} alt="img-delete" className='delete' /></button>
                                    </td>
                                </tr>
                            </tbody>
                        ))}
                    </table>
                </div>
            </>
        )}
        {editTask && (
            <Task editTaskId={editTaskId} setLoading={setLoading} setEditTask={setEditTask} isEdit={true} />)}
    </div>

);
}


export default TaskSelect