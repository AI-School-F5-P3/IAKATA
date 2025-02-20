import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { postResult, getOneResult, updateResult } from '../../services/resultServices';
import './css/Forms.css';
import Swal from 'sweetalert2';

const Result = ({ editResultId, editExperimentId, setLoading, setEditResult, setCreateResult, isEdit = false }) => {
    const { register, handleSubmit, formState: { errors }, setValue } = useForm();
    const [resultData, setResultData] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            if (isEdit && editResultId) {
                try {
                    const response = await getOneResult(editResultId);
                    const data = response.data;
                    setResultData(data);
                    setValue('description', data.description);
                    setValue('date', data.date);
                    setValue('analysis', data.analysis);
                    setValue('expected_results', data.expected_results);
                    setValue('results_obtained', data.results_obtained);
                    setValue('conclusion', data.conclusion);
                    setValue('next_step', data.next_step);
                } catch (error) {
                    console.error('Error fetching result:', error);
                }
            }
        };
        fetchData();
    }, [isEdit, editResultId, setValue]);

    const onSubmit = async (data) => {
        try {
            const formData = {
                ...data,
                experiment_id: isEdit ? resultData.experiment_id : editExperimentId
            };

            if (isEdit) {
                await updateResult(editResultId, formData);
                Swal.fire('¡Resultado actualizado correctamente!');
                setEditResult(false);
            } else {
                await postResult(formData);
                Swal.fire('¡Resultado creado correctamente!');
                setCreateResult(false);
            }
            setLoading(true);
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: `Error al ${isEdit ? 'actualizar' : 'crear'} el resultado`
            });
        }
    };

    const handleClose = () => {
        isEdit ? setEditResult(false) : setCreateResult(false);
    };

    return (
        <div className="form-container">
            <form className='form-create' onSubmit={handleSubmit(onSubmit)}>
                <h2>{isEdit ? 'EDITAR' : 'CREAR'} RESULTADO</h2>
                <div className='items'>
                    <label className='label-item'>Descripción:</label>
                    <textarea 
                        rows="10" 
                        cols="50" 
                        {...register('description', { required: 'La descripción es requerida' })} 
                    />
                    {errors.description && <p className="error-message">{errors.description.message}</p>}
                </div>
                <div className='items'>
                    <label className='label-item'>Fecha:</label>
                    <div className='date-input-wrapper'>
                        <input 
                            type="date" 
                            {...register('date', { required: 'La fecha es requerida' })} 
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.date && <p className="error-message">{errors.date.message}</p>}
                </div>
                <div className='items'>
                    <label className='label-item'>Análisis:</label>
                    <input 
                        type="text" 
                        {...register('analysis', { required: 'El análisis es requerido' })} 
                    />
                    {errors.analysis && <p className="error-message">{errors.analysis.message}</p>}
                </div>
                <div className='items'>
                    <label className='label-item'>Resultados previstos:</label>
                    <input 
                        type="text" 
                        {...register('expected_results', { required: 'Los resultados previstos son requeridos' })} 
                    />
                    {errors.expected_results && <p className="error-message">{errors.expected_results.message}</p>}
                </div>
                <div className='items'>
                    <label className='label-item'>Resultados obtenidos:</label>
                    <input 
                        type="text" 
                        {...register('results_obtained', { required: 'Los resultados obtenidos son requeridos' })} 
                    />
                    {errors.results_obtained && <p className="error-message">{errors.results_obtained.message}</p>}
                </div>
                <div className='items'>
                    <label className='label-item'>Conclusión:</label>
                    <input 
                        type="text" 
                        {...register('conclusion', { required: 'La conclusión es requerida' })} 
                    />
                    {errors.conclusion && <p className="error-message">{errors.conclusion.message}</p>}
                </div>
                <div className='items'>
                    <label className='label-item'>Siguiente paso:</label>
                    <input 
                        type="text" 
                        {...register('next_step', { required: 'El siguiente paso es requerido' })} 
                    />
                    {errors.next_step && <p className="error-message">{errors.next_step.message}</p>}
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

export default Result;