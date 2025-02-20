import { useState, useEffect } from "react";
import { getOneHypothesis, updateHypothesis, postHypothesis } from "../../services/hypothesisServices";
import { useForm } from "react-hook-form";
import { useWebSocket } from "../../context/SocketContext";
import "./css/Forms.css";
import Swal from 'sweetalert2';
import PropTypes from 'prop-types';

const Hypothesis = ({ editHypothesisId, editObstacleId, setLoading, setEditHypothesis, isEdit = false }) => {
    const { register, formState: { errors }, handleSubmit, setValue } = useForm();
    const [hypothesisData, setHypothesisData] = useState(null);
    const { WS_EVENTS, sendMessage } = useWebSocket();


    useEffect(() => {
        const fetchHypothesis = async () => {
            if (isEdit && editHypothesisId) {
                try {
                    const response = await getOneHypothesis(editHypothesisId);
                    const data = response.data;
                    setHypothesisData(data);
                    setValue("description", data.description);
                    setValue("plan_date", data.plan_date);
                    setValue("state_hypothesis", data.state_hypothesis);
                } catch (error) {
                    console.error('Error fetching hypothesis:', error);
                }
            }
        };
        fetchHypothesis();
    }, [isEdit, editHypothesisId, setValue]);

  const onSubmit = async (data) => {
        try {
            setLoading(true);
            const formData = {
                description: data.description,
                plan_date: data.plan_date,
                state_hypothesis: data.state_hypothesis,
                obstacle_id: isEdit ? hypothesisData.obstacle_id : editObstacleId,
                userId: 1
            };
    
            const response = await (isEdit ? 
                updateHypothesis(editHypothesisId, formData) : 
                postHypothesis(formData)
            );
    
            if (response?.data) {
                sendMessage(WS_EVENTS.HYPOTHESIS, {
                    id: isEdit ? editHypothesisId : response.data.id,
                    ...formData,
                    type: isEdit ? 'update' : 'create',
                    timestamp: Date.now(),
                    broadcast: true 
                });
    
                Swal.fire({
                    icon: 'success',
                    title: `Hipótesis ${isEdit ? 'actualizada' : 'creada'} correctamente!`,
                    showConfirmButton: false,
                    timer: 1500,
                    confirmButtonColor: "#002661",
                    background: '#ECF0F1',
                    customClass: {
                        popup: 'swal-custom-popup',
                        title: 'swal-custom-title',
                        content: 'swal-custom-content',
                        confirmButton: 'swal-custom-confirm'
                    }
                });
    
                setEditHypothesis(false);
            }
        } catch (error) {
            console.error("Error:", error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: `Error al ${isEdit ? 'actualizar' : 'crear'} la hipótesis`,
                confirmButtonColor: "#002661",
                background: '#ECF0F1',
                customClass: {
                    popup: 'swal-custom-popup',
                    title: 'swal-custom-title',
                    content: 'swal-custom-content',
                    confirmButton: 'swal-custom-confirm'
                }
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-container">
            <form className="form-create" onSubmit={handleSubmit(onSubmit)}>
                <h2>{isEdit ? 'EDITAR' : 'CREAR'} HIPÓTESIS</h2>
                <div className="items">
                    <label className="label-item">Descripción</label>
                    <textarea
                        rows="10"
                        cols="50"
                        {...register("description", { 
                            required: "La descripción es requerida" 
                        })}
                    />
                    {errors.description && (
                        <p className="error-message">{errors.description.message}</p>
                    )}
                </div>
                <div className="items">
                    <label className="label-item">Fecha de planificación</label>
                    <div className='date-input-wrapper'>
                        <input 
                            type="date" 
                            {...register("plan_date", { 
                                required: "La fecha de planificación es requerida" 
                            })}
                        />
                        <span className='date-icon'>&#x1F4C5;</span>
                    </div>
                    {errors.plan_date && (
                        <p className="error-message">{errors.plan_date.message}</p>
                    )}
                </div>
                <div className="items">
                    <label className="label-item">Estado de la hipótesis</label>
                    <input
                        type="text"
                        {...register("state_hypothesis", { 
                            required: "El estado de la hipótesis es requerido" 
                        })}
                    />
                    {errors.state_hypothesis && (
                        <p className="error-message">{errors.state_hypothesis.message}</p>
                    )}
                </div>
                <button className="button-forms" type="submit">
                    {isEdit ? 'Guardar' : 'Crear'}
                </button>
                <button
                    type="button"
                    className="button-forms"
                    onClick={() => setEditHypothesis(false)}
                >
                    Cerrar
                </button>
                <button className='button-forms'>MEJORAR CON IA 🪄</button>
            </form>
        </div>
    );
};
Hypothesis.propTypes = {
    editHypothesisId: PropTypes.number,
    editObstacleId: PropTypes.number.isRequired,
    setLoading: PropTypes.func.isRequired,
    setEditHypothesis: PropTypes.func.isRequired,
    isEdit: PropTypes.bool
};

export default Hypothesis;