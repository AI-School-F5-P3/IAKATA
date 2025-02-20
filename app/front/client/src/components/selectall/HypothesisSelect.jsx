import { useState, useEffect } from "react";
import {
  getHypothesis,
  deleteHypothesis,
} from "../../services/hypothesisServices";
import "./css/SelectAll.css";
import update from "../../assets/img/EditButton.svg";
import delte from "../../assets/img/delete.svg";
import Experiment from "../forms/Experiment";
import Hypothesis from "../forms/Hypothesis";
import ExperimentsSelect from "./ExperimentsSelect";
import addExpLogo from "../../assets/img/experienceButton.svg";
import { useWebSocket } from "../../context/SocketContext";
import { useSocket } from "../../utils/UseSocket";
import Swal from "sweetalert2";

const HypothesisSelect = ({ obstacle }) => {
  const [hypothesis, setHypothesis] = useState([]);
  const [editHypothesis, setEditHypothesis] = useState(false);
  const [loading, setLoading] = useState(false);
  const [editHypothesisId, setEditHypothesisId] = useState();
  const [editExperiment, setEditExperiment] = useState(false);
  const { WS_EVENTS, sendMessage } = useWebSocket();

  useEffect(() => {
    const fetchHypothesis = async () => {
      try {
        const arrayObstacleId = [];
        const hypothesisData = await getHypothesis();
        obstacle.map((item) => {
          const obstacleId = item.id;
          arrayObstacleId.push(obstacleId);
        });
        const arrayHypothesisFiltered = [];
        arrayObstacleId.map((obstacleId) => {
          const hipothesisfiltered = hypothesisData.filter(
            (state) => state.obstacle_id === obstacleId
          );
          arrayHypothesisFiltered.push(...hipothesisfiltered);
        });
        setHypothesis(arrayHypothesisFiltered);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching Challenges:", error);
      }
    };

    fetchHypothesis();
  }, [obstacle, loading]);

useSocket(WS_EVENTS.HYPOTHESIS, null, (payload) => {
  console.log("WebSocket payload:", payload);

  if (Array.isArray(payload)) {
    const filteredHypothesis = payload.filter((hyp) =>
      obstacle.some((obs) => obs.id === hyp.obstacle_id)
    );
    setHypothesis(filteredHypothesis);
    return;
  }

  setHypothesis((prev) => {
    if (payload.deleted || payload.type === 'delete') {
      return prev.filter((hyp) => hyp.id !== payload.id);
    }

    const exists = prev.some((hyp) => hyp.id === payload.id);
    const belongsToObstacle = obstacle.some(
      (obs) => obs.id === payload.obstacle_id
    );

    if (exists) {
      return prev.map((hyp) =>
        hyp.id === payload.id ? { ...payload, type: undefined } : hyp
      );
    }

    return belongsToObstacle ? [...prev, payload] : prev;
  });
});

const handleDelete = async (id) => {
  try {
    const result = await Swal.fire({
      title: "¿Estás seguro?",
      text: "Esta acción no se puede deshacer",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#002661",
      cancelButtonColor: "#dc3545",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
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
      const response = await deleteHypothesis(id);

      if (response?.status === 200) {
        sendMessage(WS_EVENTS.HYPOTHESIS, {
          id,
          type: 'delete',
          deleted: true,
          timestamp: Date.now(),
          broadcast: true
        });

        Swal.fire({
          icon: "success",
          title: "Hipótesis eliminada correctamente",
          showConfirmButton: false,
          timer: 1500,
          background: '#ECF0F1',
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
    console.error("Error:", error);
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "Error al eliminar la hipótesis",
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

  return (
    <div className="container-challenge">
      {hypothesis.length > 0 && (
        <>
          <h3>HIPOTESIS</h3>
          <div className="centered-table">
            <table className="container-table">
              {hypothesis.map((hypothes) => (
                <tbody key={hypothes.id}>
                  <tr className="tr-table">
                    <td className="title-table">Hipotesis ID</td>
                    <td className="tr-table">{hypothes.id}</td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">Descripción</td>
                    <td className="tr-table">{hypothes.description}</td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">Fecha de plan</td>
                    <td className="tr-table">{hypothes.plan_date}</td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">Estado de la hipotesis</td>
                    <td className="tr-table">{hypothes.state_hypothesis}</td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">Obtaculo ID</td>
                    <td className="tr-table">{hypothes.obstacle_id}</td>
                  </tr>
                  <tr className="tr-table">
                    <td className="title-table">Acciones</td>
                    <td className="container-button">
                      <button
                        title="Editar"
                        className="CardActionButtonContainer"
                        onClick={() => {
                          setEditHypothesisId(hypothes.id),
                            setEditHypothesis(true);
                        }}
                      >
                        <img src={update} className="edit" />
                      </button>
                      <button
                        title="Añadir experimento"
                        className="CardActionButtonContainer"
                        onClick={() => {
                          setEditHypothesisId(hypothes.id),
                            setEditExperiment(true);
                        }}
                      >
                        <img src={addExpLogo} />
                      </button>
                      <button
                        title="Eliminar"
                        className="CardActionButtonContainer"
                        onClick={() => handleDelete(hypothes.id)}
                      >
                        <img src={delte} alt="delete" className="delete" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              ))}
            </table>
          </div>
        </>
      )}
      {editHypothesis && (
        <Hypothesis
          isEdit={true}
          editHypothesisId={editHypothesisId}
          setLoading={setLoading}
          setEditHypothesis={setEditHypothesis}
        />
      )}
      {editExperiment && (
        <Experiment
          isEdit={false}
          editHypothesisId={editHypothesisId}
          setLoading={setLoading}
          setEditExperiment={setEditExperiment}
        />
      )}
      <ExperimentsSelect hypothesis={hypothesis} />
    </div>
  );
};

export default HypothesisSelect;
