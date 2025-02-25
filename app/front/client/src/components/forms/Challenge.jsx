import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { postChallenge, getOneChallenge, updateChallenge } from '../../services/challengeServices';
import { useWebSocket } from '../../context/SocketContext';
import { useForm } from 'react-hook-form';
import Swal from 'sweetalert2';
import './css/Forms.css';
import PropTypes from 'prop-types';

import ImproveWithAIButton from '../buttonIa/ImproveWithAIButton';

const Challenge = ({ challengeId, setLoading, setEditable, isEdit = false }) => {
    const { getValues, handleSubmit, register, formState: { errors }, watch, setValue, reset, trigger } = useForm({defaultValues: {
        description: ''
    }});
    const navigate = useNavigate();
    const [isImproving, setIsImproving] = useState(false);
    const [challengeData, setChallengeData] = useState({});
    const { socket, isConnected, WS_EVENTS } = useWebSocket();

    const startDate = watch('start_date');
    const endDate = watch('end_date');

    const idForm = "RE";

    // useEffect(() => {
    //     if (!socket || !isConnected) return;

    //     const handleWebSocketMessage = (event) => {
    //         try {
    //             const data = JSON.parse(event.data);
    //             if (data.type === WS_EVENTS.CHALLENGE && data.payload.id === challengeId) {
    //                 setChallengeData(prevData => ({...prevData, ...data.payload}));
    //                 Object.entries(data.payload).forEach(([key, value]) => {
    //                     setValue(key, value);
    //                 });
    //             }
    //         } catch (error) {
    //             console.error('WebSocket message error:', error);
    //         }
    //     };

    //     socket.addEventListener('message', handleWebSocketMessage);
    //     return () => {
    //         if (socket?.readyState === WebSocket.OPEN) {
    //             socket.removeEventListener('message', handleWebSocketMessage);
    //         }
    //     };
    // }, [socket, isConnected, challengeId, setValue, WS_EVENTS]);

    useEffect(() => {
        if (!socket || !isConnected) return;
    
        const handleWebSocketMessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                const currentPath = window.location.pathname;
                const messagePath = data.payload?.path;
    
                if (messagePath !== currentPath) return;
    
                if (data.type === WS_EVENTS.CHALLENGE && data.payload.id === challengeId) {
                    setChallengeData(prevData => ({...prevData, ...data.payload}));
                    Object.entries(data.payload).forEach(([key, value]) => {
                        setValue(key, value);
                    });
                }
            } catch (error) {
                console.error('WebSocket message error:', error);
            }
        };
    
        socket.addEventListener('message', handleWebSocketMessage);
        return () => {
            socket.removeEventListener('message', handleWebSocketMessage);
        };
    }, [socket, isConnected, challengeId, setValue, WS_EVENTS]);

    useEffect(() => {
        if (isEdit && challengeId) {
            const fetchData = async () => {
                try {
                    const response = await getOneChallenge(challengeId);
                    const data = response.data;
                    setChallengeData(data);
                    Object.entries(data).forEach(([key, value]) => {
                        setValue(key, value);
                    });
                } catch (error) {
                    console.error('Error fetching challenge:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Error al cargar el reto',
                        customClass: {
                            popup: 'swal-custom-popup',
                            title: 'swal-custom-title',
                            text: 'swal-custom-text',
                        }
                    });
                }
            };
            fetchData();
        }
    }, [challengeId, setValue, isEdit]);


    useEffect(() => {
        return () => {
            reset();
            setChallengeData({});
        };
    }, [reset]);


    const validateDateRange = () => {
        if (startDate && endDate) {
            return new Date(startDate) <= new Date(endDate) || 
                "La fecha de inicio no puede ser posterior a la fecha de fin";
        }
    };

    const validateText = (value) => {
        return (value && typeof value === 'string') || "Por favor, introduce texto";
    };

    const onSubmit = async (data) => {
        console.log('data', data);
        try {
            if (isEdit) {
                await updateChallenge(challengeId, data);
                Swal.fire({
                    icon: 'success',
                    title: '¡Actualizado correctamente!',
                    text: 'Los datos han sido actualizados correctamente',
                    customClass: {
                        popup: "swal-custom-popup",
                        title: "swal-custom-title",
                        text: "swal-custom-text",
                    }
                });
                setLoading(true);
                setEditable(false);
            } else {
                const response = await postChallenge(data);
                if (response?.data?.id) {
                        Swal.fire({
                            icon: 'success',
                            title: '¡Éxito!',
                            text: '¿Deseas crear el estado actual?',
                            showCancelButton: true,
                            confirmButtonText: 'Sí, crear estado actual',
                            cancelButtonText: 'No, más tarde',
                            confirmButtonColor: "#002661",
                            background: '#ECF0F1',
                            customClass: {
                                popup: "swal-custom-popup",
                                title: "swal-custom-title",
                                content: "swal-custom-content",
                                confirmButton: "swal-custom-confirm",
                                cancelButton: "swal-custom-cancel"
                            }
                        })
                    .then((result) => {
                        if (result.isConfirmed) {
                            navigate(`/home/card/${response.data.id}`);
                        } else {
                            navigate('/home');
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Form submission error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: `Error al ${isEdit ? 'actualizar' : 'crear'} el reto`,
                customClass: {
                    popup: "swal-custom-popup",
                    title: "swal-custom-title",
                    confirmButton: "swal-custom-confirm",
                }
            });
        }
    };

    const handleClose = () => isEdit ? setEditable(false) : navigate('/home');

    // const handleImproveResult = (improvedData) => {
    //     console.log('Datos mejorados:', improvedData);
    //     setValue('description', improvedData.description); // Actualiza el campo de descripción
    // };
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
        <div className={isEdit ? "form-container" : "form-box"}>
            <form className='form-create' onSubmit={handleSubmit(onSubmit)}>
                <h2>{isEdit ? "EDITAR RETO" : "CREAR RETO"}</h2>
                
                <div className='items'>
                    <label className='label-item'>Nombre</label>
                    <input 
                        type="text" 
                        {...register('name', { 
                            required: "El nombre es requerido",
                            validate: validateText 
                        })} 
                    />
                    {errors.name && <p className="error-message">{errors.name.message}</p>}
                </div>

                {/* <div className='items'>
                    <label className='label-item'>Descripción</label>
                    <textarea 
                        rows="10" 
                        cols="50" 
                        {...register('description', { 
                            required: 'La descripción es requerida', 
                            validate: validateText 
                        })} 
                    />
                    {errors.description && <p className="error-message">{errors.description.message}</p>}
                </div> */}
                <div className='items'>
                    <label className='label-item'>Descripción</label>
                    <textarea 
                        rows="10" 
                        cols="50" 
                        {...register('description', { 
                            required: 'La descripción es requerida', 
                            validate: validateText 
                        })} 
                        disabled={isImproving}
                        placeholder={isImproving ? "Mejorando descripción con IA..." : "Escribe una descripción o usa el botón de IA para mejorarla"}
                        value={watch('description')}
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
                    <label className='label-item'>Fecha de inicio:</label>
                    <div className='date-input-wrapper'>
                        <input 
                            type="date" 
                            {...register('start_date', { 
                                required: "La fecha de inicio es requerida", 
                                validate: validateDateRange 
                            })} 
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.start_date && <p className="error-message">{errors.start_date.message}</p>}
                </div>

                <div className='items'>
                    <label className='label-item'>Fecha de fin:</label>
                    <div className='date-input-wrapper'>
                        <input 
                            type="date" 
                            {...register('end_date', { 
                                required: "La fecha de fin es requerida"
                            })} 
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.end_date && <p className="error-message">{errors.end_date.message}</p>}
                </div>

                <div className='button-group'>
                    <button className='button-forms' type="submit">
                        {isEdit ? "GUARDAR" : "CREAR"}
                    </button>
                    <button 
                        type="button"
                        className='button-forms' 
                        onClick={handleClose}
                    >
                        {isEdit ? "CANCELAR" : "VOLVER"}
                    </button>
                    {/* <ImproveWithAIButton
                        className="button-forms"
                        getValues={() => ({
                            idForm,
                            ...getValues(["name", "description"])
                        })}
                        onResult={handleImproveResult} 
                    /> */}
                    <ImproveWithAIButton
                        className="button-forms"
                        getValues={() => ({
                            idForm,
                            ...getValues(["name", "description"])
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
Challenge.propTypes = {
    challengeId: PropTypes.string.isRequired,
    setLoading: PropTypes.func.isRequired,
    setEditable: PropTypes.func.isRequired,
    isEdit: PropTypes.bool
};

export default Challenge;