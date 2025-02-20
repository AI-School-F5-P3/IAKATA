import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { postTask, getOneTask, updateTask } from '../../services/taskServices';
import './css/Forms.css';
import Swal from 'sweetalert2';

const Task = ({ editTaskId, editExperimentId, setLoading, setEditTask, setCreateTask, isEdit = false }) => {
    const { register, handleSubmit, formState: { errors, isDirty }, setValue, getValues } = useForm();
    const [taskData, setTaskData] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            if (isEdit && editTaskId) {
                try {
                    const response = await getOneTask(editTaskId);
                    const data = response.data;
                    setTaskData(data);
                    setValue("description", data.description);
                    setValue("responsible", data.responsible);
                    setValue("start_date", data.start_date);
                    setValue("end_date_prev", data.end_date_prev);
                    setValue("end_date_real", data.end_date_real);
                    setValue("state", data.state);
                } catch (error) {
                    console.error('Error fetching task:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Error al cargar los datos de la tarea'
                    });
                }
            }
        };
        fetchData();
    }, [isEdit, editTaskId, setValue]);

    const compareDates = (date1, date2) => {
        return new Date(date1) > new Date(date2);
    };

    const validateEndDate = (value) => {
        const startDate = getValues('start_date');
        return compareDates(value, startDate) || "La fecha final debe ser posterior a la fecha de inicio";
    };

    const validateRealEndDate = (value) => {
        const startDate = getValues('start_date');
        const endDatePrev = getValues('end_date_prev');
        return (compareDates(value, startDate) && compareDates(value, endDatePrev)) ||
            "La fecha real debe ser posterior a la fecha de inicio y a la fecha final prevista";
    };

    const onSubmit = async (data) => {
        try {
            console.log("Data:", data);
            const formData = {
                ...data,
                experiment_id: isEdit ? taskData?.experiment_id : editExperimentId
            };

            if (isEdit) {
                await updateTask(editTaskId, formData);
                Swal.fire('¡Tarea actualizada correctamente!');
                setEditTask(false);
            } else {
                await postTask(formData);
                Swal.fire('¡Tarea creada correctamente!');
                setCreateTask(false);
            }
            setLoading(true);
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: `Error al ${isEdit ? 'actualizar' : 'crear'} la tarea`
            });
        }
    };

    const handleClose = () => {
        isEdit ? setEditTask(false) : setCreateTask(false);
    };

    return (
        <div className="form-container">
            <form className='form-create' onSubmit={handleSubmit(onSubmit)}>
                <h2>{isEdit ? 'EDITAR' : 'CREAR'} TAREA</h2>
                <div className='items'>
                    <label className='label-item'>Descripción:</label>
                    <textarea
                        rows="10"
                        cols="50"
                        {...register('description', { required: true })}
                    />
                    {errors.description &&
                        <p className="error-message">La descripción es requerida</p>
                    }
                </div>
                <div className='items'>
                    <label className='label-item'>Responsable:</label>
                    <input
                        type="text"
                        {...register('responsible', { required: true })}
                    />
                    {errors.responsible &&
                        <p className="error-message">El responsable es requerido</p>
                    }
                </div>
                <div className='items'>
                    <label className='label-item'>Fecha de inicio:</label>
                    <div className='date-input-wrapper'>
                        <input
                            type="date"
                            {...register('start_date', { required: true })}
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.start_date &&
                        <p className="error-message">La fecha de inicio es requerida</p>
                    }
                </div>
                <div className='items'>
                    <label className='label-item'>Fecha final prevista:</label>
                    <div className='date-input-wrapper'>
                        <input
                            type="date"
                            {...register('end_date_prev', {
                                required: true,
                                validate: validateEndDate
                            })}
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.end_date_prev &&
                        <p className="error-message">{errors.end_date_prev.message}</p>
                    }
                </div>
                <div className='items'>
                    <label className='label-item'>Fecha real:</label>
                    <div className='date-input-wrapper'>
                        <input
                            type="date"
                            {...register('end_date_real', {
                                required: true,
                                validate: validateRealEndDate
                            })}
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.end_date_real &&
                        <p className="error-message">{errors.end_date_real.message}</p>
                    }
                </div>
                <div className='items'>
                    <label className='label-item'>Estado:</label>
                    <input
                        type="text"
                        {...register('state', { required: true })}
                    />
                    {errors.state &&
                        <p className="error-message">El estado es requerido</p>
                    }
                </div>
                <button
                    className='button-forms'
                    type="submit"
                    disabled={!isEdit && !isDirty}
                >
                    {isEdit ? 'Guardar' : 'Enviar'}
                </button>
                <button
                    className='button-forms'
                    type="button"
                    onClick={handleClose}
                >
                    Cerrar
                </button>
                <button className='button-forms'>MEJORAR CON IA 🪄</button>
            </form>
        </div>
    );
};

export default Task;