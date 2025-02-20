import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { postLearning, getOneLearning, updateLearning } from '../../services/learningsServices';
import './css/Forms.css';
import Swal from 'sweetalert2';

const Learning = ({ editLearningId, editResultId, setLoading, setEditLearning, setCreateLearning, isEdit = false }) => {
    const { register, handleSubmit, formState: { errors }, setValue } = useForm();
    const [learningData, setLearningData] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            if (isEdit && editLearningId) {
                try {
                    const response = await getOneLearning(editLearningId);
                    const data = response.data;
                    setLearningData(data);
                    setValue('description', data.description);
                    setValue('learning_date', data.learning_date);
                } catch (error) {
                    console.error('Error fetching learning:', error);
                }
            }
        };
        fetchData();
    }, [isEdit, editLearningId, setValue]);

    const onSubmit = async (data) => {
        try {
            const formData = {
                ...data,
                results_id: isEdit ? learningData.results_id : editResultId
            };

            if (isEdit) {
                await updateLearning(editLearningId, formData);
                Swal.fire('¡Aprendizaje actualizado correctamente!');
                setEditLearning(false);
            } else {
                await postLearning(formData);
                Swal.fire('¡Aprendizaje creado correctamente!');
                setCreateLearning(false);
            }
            setLoading(true);
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: `Error al ${isEdit ? 'actualizar' : 'crear'} el aprendizaje`
            });
        }
    };

    const handleClose = () => {
        isEdit ? setEditLearning(false) : setCreateLearning(false);
    };

    return (
        <div className="form-container">
            <form className='form-create' onSubmit={handleSubmit(onSubmit)}>
                <h2>{isEdit ? 'EDITAR' : 'CREAR'} APRENDIZAJE</h2>
                <div className='items'>
                    <label className='label-item'>Descripción:</label>
                    <textarea 
                        rows="10" 
                        cols="50" 
                        {...register('description', { 
                            required: 'La descripción es requerida' 
                        })} 
                    />
                    {errors.description && 
                        <p className="error-message">{errors.description.message}</p>
                    }
                </div>
                <div className='items'>
                    <label className='label-item'>Fecha de aprendizaje:</label>
                    <div className='date-input-wrapper'>
                        <input 
                            type="date" 
                            {...register('learning_date', { 
                                required: 'La fecha es requerida' 
                            })} 
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.learning_date && 
                        <p className="error-message">{errors.learning_date.message}</p>
                    }
                </div>
                <button className='button-forms' type="submit">
                    {isEdit ? 'Guardar' : 'Enviar'}
                </button>
                <button 
                    type="button" 
                    className='button-forms' 
                    onClick={handleClose}
                >
                    Cerrar
                </button>
                <button className='button-forms'>MEJORAR CON IA 🪄</button>
            </form>
        </div>
    );
};

export default Learning;