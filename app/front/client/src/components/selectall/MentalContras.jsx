import { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import {
  getMentalContrast,
  deleteMentalContrast,
} from "../../services/mentalContrastServices";
import update from "../../assets/img/EditButton.svg";
import "./css/SelectAll.css";
import delte from "../../assets/img/delete.svg";
import ContrastMental from "../forms/CreateContrastMental";
import { useSocket } from "../../utils/UseSocket";
import { useWebSocket } from "../../context/SocketContext";
import Swal from "sweetalert2";

const MentalContras = ({ targetState, editTargetId }) => {
  const [mentalContrasts, setMentalContrasts] = useState([]);
  const [editMental, setEditMental] = useState(false);
  const [editMentalId, setEditMentalId] = useState();
  const [loading, setLoading] = useState(false);
  const { WS_EVENTS, sendMessage } = useWebSocket();

  useSocket(
    WS_EVENTS.MENTAL_CONTRAST,
    editTargetId,
    useCallback(
      (payload) => {
        if (!payload) return;

        if (Array.isArray(payload)) {
          if (payload.length === 0) return;

          const filteredContrasts = payload.filter(
            (contrast) =>
              contrast &&
              contrast.target_state_id &&
              targetState.some((ts) => ts.id === contrast.target_state_id)
          );

          if (filteredContrasts.length > 0) {
            setMentalContrasts(filteredContrasts);
          }
        } else {
          setMentalContrasts((prev) => {
            if (payload.deleted) {
              return prev.filter((mc) => mc.id !== payload.id);
            }

            const exists = prev.some((mc) => mc.id === payload.id);
            const belongsToTarget = targetState.some(
              (ts) => ts.id === payload.target_state_id
            );

            if (!belongsToTarget) return prev;

            return exists
              ? prev.map((mc) => (mc.id === payload.id ? payload : mc))
              : [...prev, payload];
          });
        }
      },
      [targetState]
    )
  );

  useEffect(() => {
    const fetchMentalContrast = async () => {
      try {
        const arrayTargetStaId = [];
        const mentalContrastsData = await getMentalContrast();
        targetState.map((item) => {
          const targetId = item.id;
          arrayTargetStaId.push(targetId);
        });
        const arrayMentalContratFiltered = [];
        arrayTargetStaId.map((targetId) => {
          const mentalContrastfilteredData = mentalContrastsData.filter(
            (contrast) => contrast.target_state_id === targetId
          );
          arrayMentalContratFiltered.push(...mentalContrastfilteredData);
        });
        setMentalContrasts(arrayMentalContratFiltered);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching Challenges:", error);
      }
    };

    fetchMentalContrast();
  }, [targetState, loading]);

  const handleDelete = async (mentalId) => {
    try {
      const result = await Swal.fire({
        title: "¿Estás seguro?",
        text: "Esta acción no se puede deshacer",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#002661",
        cancelButtonColor: "#ECF0F1",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
        background: "#ECF0F1",
        customClass: {
          popup: "swal-custom-popup",
          title: "swal-custom-title",
          content: "swal-custom-content",
          confirmButton: "swal-custom-confirm",
          cancelButton: "swal-custom-cancel",
        },
      });

      if (result.isConfirmed) {
        const response = await deleteMentalContrast(mentalId);
        if (response) {
          sendMessage(WS_EVENTS.MENTAL_CONTRAST, {
            id: mentalId,
            deleted: true,
            timestamp: Date.now(),
          });
          setLoading(true);
        }
      }
    } catch (error) {
      Swal.fire({
        title: "Error",
        text:
          error.response?.data?.message ||
          "No se pudo eliminar el contraste mental",
        icon: "error",
        customClass: {
          popup: "swal-custom-popup",
          title: "swal-custom-title",
          content: "swal-custom-content",
          confirmButton: "swal-custom-confirm",
        },
      });
    }
  };

  const handleCloseModal = useCallback(() => {
    setEditMentalId(null);
    setEditMental(false);
  }, []);

  const handleEditClick = useCallback((mentalId) => {
    if (!mentalId) return;
    setEditMentalId(mentalId);
    setEditMental(true);
  }, []);

  return (
    <div className="container-challenge">
      {mentalContrasts.length > 0 && (
        <>
          <h3>CONTRASTE MENTAL</h3>
          <div className="centered-table">
            <table className="container-table">
              {mentalContrasts.map((mentalContrast) => (
                <tbody key={mentalContrast.id}>
                  <tr className="tr-table">
                    <td className="title-table">Contraste mental ID</td>
                    <td className="tr-table">{mentalContrast.id}</td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">Puntuación</td>
                    <td className="tr-table">{mentalContrast.points}</td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">Fecha de evaluacion</td>
                    <td className="tr-table">
                      {mentalContrast.evaluation_date}
                    </td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">EOID</td>
                    <td className="tr-table">
                      {mentalContrast.target_state_id}
                    </td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">Acciones</td>
                    <td className="container-button">
                      <button
                        title="Editar"
                        className="CardActionButtonContainer"
                        onClick={() => handleEditClick(mentalContrast.id)}
                      >
                        <img
                          src={update}
                          alt="logo-update"
                          className="logo-edit"
                        />
                      </button>
                      <button
                        title="Eliminar"
                        className="CardActionButtonContainer"
                        onClick={() => handleDelete(mentalContrast.id)}
                      >
                        <img src={delte} alt="img-delete" className="delete" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              ))}
            </table>
          </div>
        </>
      )}
      {editMental && (
        <ContrastMental
          editMentalId={editMentalId}
          editTargetId={editTargetId}
          setLoading={setLoading}
          setEditMental={handleCloseModal}
          isEdit={true}
        />
      )}
    </div>
  );
};

MentalContras.propTypes = {
  targetState: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
    })
  ).isRequired,
  editTargetId: PropTypes.number.isRequired,
};

export default MentalContras;