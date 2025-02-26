import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useWebSocket } from '../../context/SocketContext';
import { useSocket } from '../../utils/UseSocket';
import { getOneTargetState, postTargetState, updateTargetState } from '../../services/targetStateServices';
import PropTypes from 'prop-types';
import Swal from 'sweetalert2';
import './css/Forms.css';

import ImproveWithAIButton from '../buttonIa/ImproveWithAIButton';

const TargetState = ({ challengeId, targetStateId, setLoading, setEditTargetState, setCreateTarget, isEdit = false }) => {
    const { register, handleSubmit, formState: { errors }, setValue, getValues } = useForm();
    const [targetStateData, setTargetStateData] = useState({});
    const { WS_EVENTS, sendMessage } = useWebSocket();
    const [isImproving, setIsImproving] = useState(false);

    const idForm = "TA";

    useSocket(
        WS_EVENTS.TARGET_STATE,
        targetStateId,
        (payload) => {
            if (payload.id === targetStateId) {
                setTargetStateData(payload);
                setValue('description', payload.description);
                setValue('start_date', payload.start_date);
                setValue('date_goal', payload.date_goal);
            }
        }
    );

    useEffect(() => {
        if (isEdit && targetStateId) {
            const fetchData = async () => {
                try {
                    const response = await getOneTargetState(targetStateId);
                    setTargetStateData(response.data);
                } catch (error) {
                    console.error('Error fetching target state:', error);
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo cargar el estado objetivo',
                        icon: 'error',
                        confirmButtonColor: "#002661",
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
            fetchData();
        }
    }, [isEdit, targetStateId]);

    const validateDate = (value) => {
        const startDate = document.querySelector('input[name="start_date"]').value;
        return value > startDate || 'La fecha de meta debe ser posterior a la fecha de inicio';
    };

    const onSubmit = async (data) => {
        try {
            const formData = {
                description: data.description,
                start_date: data.start_date,
                date_goal: data.date_goal,
                challenge_id: challengeId
            };
    
            const response = await (isEdit ? 
                updateTargetState(targetStateId, formData) : 
                postTargetState(formData)
            );
    
            if (response) {
                sendMessage(WS_EVENTS.TARGET_STATE, {
                    ...response,
                    type: isEdit ? 'update' : 'create',
                    timestamp: Date.now()
                });
                
                Swal.fire({
                    icon: 'success',
                    title: `Estado objetivo ${isEdit ? 'actualizado' : 'creado'} correctamente!`,
                    showConfirmButton: false,
                    timer: 1500,
                    background: '#ECF0F1',
                    customClass: {
                        popup: 'swal-custom-popup',
                        title: 'swal-custom-title',
                        content: 'swal-custom-content',
                    }
                });
                
                setLoading(true);
                setEditTargetState(false);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al guardar el estado objetivo',
                confirmButtonColor: "#002661",
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

    const handleClose = () => isEdit ? setEditTargetState(false) : (setCreateTarget && setCreateTarget(false)) || setEditTargetState(false);

    const handleImproveResult = (improvedData) => {
        console.log('Datos mejorados:', improvedData.data.description);
        if (improvedData) {
            setValue('description', improvedData.data.description, {
                shouldValidate: true,
                shouldDirty: true,
                shouldTouch: true
            });
            Swal.fire({
                icon: 'success',
                title: '¡Texto mejorado!',
                text: 'La descripción ha sido mejorada con IA',
                timer: 1500,
                showConfirmButton: false
            });
        }
    };
    
    return (
        <div className={isEdit ? "form-box" : "form-container"}>
            <form className='form-create' onSubmit={handleSubmit(onSubmit)}>
                <h2>{isEdit ? "EDITAR ESTADO OBJETIVO" : "CREAR ESTADO OBJETIVO"}</h2>
                <div className='items'>
                    <label className='label-item'>Descripción: </label>
                    <textarea 
                        rows="10" 
                        cols="50" 
                        {...register('description', { 
                            required: 'La descripción es requerida', 
                        })} 
                        disabled={isImproving}
                        placeholder={isImproving ? "Mejorando descripción con IA..." : "Escribe una descripción o usa el botón de IA para mejorarla"}
                        onChange={(e) => setValue('description', e.target.value, { 
                            shouldValidate: true 
                        })}
                        style={{
                            backgroundColor: isImproving ? '#f5f5f5' : 'white',
                            cursor: isImproving ? 'wait' : 'text'
                        }}
                    />
                    {errors.description && <p className="error-message">{errors.description.message}</p>}
                </div>
                <div className='items'>
                    <label className='label-item'>Fecha de Inicio:</label>
                    <div className='date-input-wrapper'>
                        <input 
                            type="date" 
                            {...register('start_date', { required: true })} 
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.start_date && <p className="error-message">La fecha de inicio es requerida</p>}
                </div>
                <div className='items'>
                    <label className='label-item'>Fecha de Meta:</label>
                    <div className='date-input-wrapper'>
                        <input 
                            type="date" 
                            {...register('date_goal', {
                                required: true, 
                                validate: {futureDate: validateDate}
                            })} 
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.date_goal && <p className="error-message">La fecha de meta debe ser posterior a la fecha de inicio</p>}
                </div>
                <div className='container-buttons'>
                    <button type="submit" className='button-forms'>
                        {isEdit ? "ACTUALIZAR" : "CREAR"}
                    </button>
                    <button type="button" className='button-forms' onClick={handleClose}>
                        {isEdit ? "CANCELAR" : "CERRAR"}
                    </button>
                    <ImproveWithAIButton
                        className="button-forms"
                        getValues={() => ({
                            idForm,
                            ...getValues(["description"])
                        })}
                        onResult={(data) => {
                            setIsImproving(true);
                            handleImproveResult(data);
                            setIsImproving(false);
                        }}
                        disabled={isImproving}
                    />
                </div>
            </form>
        </div>
    );
};

TargetState.propTypes = {
    challengeId: PropTypes.string.isRequired,
    targetStateId: PropTypes.string,
    setLoading: PropTypes.func.isRequired,
    setEditTargetState: PropTypes.func.isRequired,
    setCreateTarget: PropTypes.func,
    isEdit: PropTypes.bool
};

export default TargetState;