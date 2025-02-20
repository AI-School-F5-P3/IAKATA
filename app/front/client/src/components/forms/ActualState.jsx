import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import {
  postActualState,
  getOneActualState,
  updateActualState,
} from "../../services/actualStateServices";
import { useWebSocket } from "../../context/SocketContext";
import Swal from "sweetalert2";
import "./css/Forms.css";

const ActualState = ({
  actualStateId,
  challengeId,
  setEditable,
  isEdit = false,
}) => {
  const {
    handleSubmit,
    register,
    formState: { errors },
    setValue,
  } = useForm();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { WS_EVENTS, sendMessage } = useWebSocket();
  const [createActual, setCreateActual] = useState(true);
  const [currentDate] = useState(new Date().toISOString().split("T")[0]);

  useEffect(() => {
    if (isEdit && actualStateId) {
      const fetchData = async () => {
        try {
          const response = await getOneActualState(actualStateId);
          if (response?.data) {
            Object.entries(response.data).forEach(([key, value]) => {
              setValue(key, value);
            });
          }
        } catch (error) {
          console.error("Error fetching:", error);
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Error al cargar el estado actual",
            confirmButtonColor: "#002661",
            background: '#ECF0F1',
            customClass: {
                popup: "swal-custom-popup",
                title: "swal-custom-title",
                content: "swal-custom-content",
                confirmButton: "swal-custom-confirm"
            }
        });
        }
      };
      fetchData();
    } else {
      setValue("date", currentDate);
    }
  }, [actualStateId, currentDate, setValue, isEdit]);

  const onSubmit = async (data) => {
    if (!data.description?.trim() || !challengeId) return;

    try {
        setIsSubmitting(true);
        console.log("data", data);
        const formData = {
            description: data.description.trim(),
            date: data.date,
            challenge_id: challengeId
        };

        const response = await (isEdit
            ? updateActualState(actualStateId, formData)
            : postActualState(formData));

        if (response?.data) {
            const wsPayload = {
                ...response.data,
                challenge_id: challengeId,
                type: isEdit ? "update" : "create",
                timestamp: Date.now(),
            };
            sendMessage(WS_EVENTS.ACTUAL_STATE, wsPayload);
            setEditable(false);

            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: `Estado actual ${isEdit ? 'actualizado' : 'creado'} correctamente`,
                customClass: {
                    popup: "swal-custom-popup",
                    title: "swal-custom-title",
                    confirmButton: "swal-custom-confirm",
                }
            });
        }
    } catch (error) {
        console.error("Form submission error:", error);
        Swal.fire({
            icon: "error",
            title: "Error",
            text: `No se pudo ${isEdit ? "actualizar" : "crear"} el estado actual`,
            customClass: {
                popup: "swal-custom-popup",
                title: "swal-custom-title",
                confirmButton: "swal-custom-confirm",
            }
        });
    } finally {
        setIsSubmitting(false);
    }
};

  return (
    <div className={isEdit ? "form-container" : "form-box"}>
      <form className="form-create" onSubmit={handleSubmit(onSubmit)}>
        <h2>{isEdit ? "EDITAR ESTADO ACTUAL" : "CREAR ESTADO ACTUAL"}</h2>
        <div className="items">
          <label className="label-item">Descripción</label>
          <textarea
            rows="10"
            cols="50"
            {...register("description", {
              required: "Este campo es requerido",
              minLength: {
                value: 10,
                message: "La descripción debe tener al menos 10 caracteres",
              },
            })}
          />
          {errors.description && (
            <p className="error-message">{errors.description.message}</p>
          )}
        </div>
        <div className="items">
          <label className="label-item">Fecha</label>
          <div className="date-input-wrapper">
            <input
              type="date"
              {...register("date", { required: "Este campo es requerido" })}
            />
            <span className="date-icon">&#x1F4C5;</span>
          </div>
          {errors.date && (
            <p className="error-message">{errors.date.message}</p>
          )}
        </div>
        <button className="button-forms" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Procesando..." : isEdit ? "GUARDAR" : "CREAR"}
        </button>
        <button
          type="button"
          className="button-forms"
          onClick={() => setEditable(false)}
          disabled={isSubmitting}
        >
          CANCELAR
        </button>
        <button className="button-forms">MEJORAR CON IA 🪄</button>
      </form>
    </div>
  );
};

ActualState.propTypes = {
  actualStateId: PropTypes.string,
  challengeId: PropTypes.string.isRequired,
  setLoading: PropTypes.func.isRequired,
  setEditable: PropTypes.func.isRequired,
  isEdit: PropTypes.bool,
};

export default ActualState;