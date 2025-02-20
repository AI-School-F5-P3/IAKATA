import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useWebSocket } from "../../context/SocketContext";
import { getOneChallenge } from "../../services/challengeServices";
import SelectAllChallenges from "../selectall/selectAllChallenges";
import TargetSta from "../selectall/TargetSta";
import SelectAllActualState from "../selectall/SelectAllActualState";
import TribeSelect from "../selectall/TribeSelect";
import "./Card.css";

const Card = () => {
  const { id } = useParams();
  const { socket, WS_EVENTS } = useWebSocket();

  const [cardState, setCardState] = useState({
    challenge: null,
    actualState: null,
    targetState: null,
    mentalContrast: null,
    obstacle: [],
    hypothesis: null,
    experiment: null,
    task: null,
    result: null,
    learning: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchChallenge = async () => {
      try {
        const data = await getOneChallenge(id);
        setCardState((prev) => ({
          ...prev,
          challenge: data,
        }));
        setLoading(false);
      } catch (error) {
        console.error("Error fetching challenge:", error);
        setError(error.message);
        setLoading(false);
      }
    };

    fetchChallenge();
  }, [id]);

  useEffect(() => {
    if (!socket) return;

    const handleWebSocketMessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        const handlers = {
          [WS_EVENTS.CHALLENGE]: (payload) => {
            if (payload.deleted) {
            } else if (payload.id === id) {
              setCardState((prev) => ({
                ...prev,
                challenge: { ...prev.challenge, ...payload },
              }));
            }
          },
          [WS_EVENTS.ACTUAL_STATE]: (payload) => {
            if (payload.challenge_id === id) {
              if (payload.deleted) {
                setCardState((prev) => ({
                  ...prev,
                  actualState: null,
                  challenge: {
                    ...prev.challenge,
                    actual_state: null,
                  },
                }));
                return;
              }
              setCardState((prev) => ({
                ...prev,
                actualState: payload,
                challenge: {
                  ...prev.challenge,
                  actual_state: payload.description,
                },
              }));
            }
          },
          [WS_EVENTS.TARGET_STATE]: (payload) => {
            if (payload.challenge_id === id) {
              setCardState((prev) => ({
                ...prev,
                targetState: payload,
              }));
            }
          },
          [WS_EVENTS.MENTAL_CONTRAST]: (payload) => {
            if (payload.challenge_id === id) {
              setCardState((prev) => ({
                ...prev,
                mentalContrast: payload,
              }));
            }
          },
          [WS_EVENTS.OBSTACLE]: (payload) => {
            if (payload.deleted) {
              setCardState((prev) => ({
                ...prev,
                obstacle: prev.obstacle.filter((obs) => obs.id !== payload.id),
              }));
            } else {
              setCardState((prev) => ({
                ...prev,
                obstacle: Array.isArray(prev.obstacle)
                  ? prev.obstacle.some((obs) => obs.id === payload.id)
                    ? prev.obstacle.map((obs) =>
                      obs.id === payload.id ? payload : obs
                    )
                    : [...prev.obstacle, payload]
                  : [payload],
              }));
            }
          },
          [WS_EVENTS.HYPOTHESIS]: (payload) => {
            if (payload.challenge_id === id) {
              setCardState((prev) => ({
                ...prev,
                hypothesis: payload,
              }));
            }
          },
          [WS_EVENTS.EXPERIMENT]: (payload) => {
            if (payload.challenge_id === id) {
              setCardState((prev) => ({
                ...prev,
                experiment: payload,
              }));
            }
          },
          [WS_EVENTS.TASK]: (payload) => {
            if (payload.challenge_id === id) {
              setCardState((prev) => ({
                ...prev,
                task: payload,
              }));
            }
          },
          [WS_EVENTS.RESULT]: (payload) => {
            if (payload.challenge_id === id) {
              setCardState((prev) => ({
                ...prev,
                result: payload,
              }));
            }
          },
          [WS_EVENTS.LEARNING]: (payload) => {
            if (payload.challenge_id === id) {
              setCardState((prev) => ({
                ...prev,
                learning: payload,
              }));
            }
          },
        };

        if (handlers[data.type]) {
          handlers[data.type](data.payload);
        }
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };

    socket.addEventListener("message", handleWebSocketMessage);
    return () => socket.removeEventListener("message", handleWebSocketMessage);
  }, [socket, id, WS_EVENTS]);

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!cardState.challenge) return <div>No se encontró el reto</div>;

  return (
    <div className="card-center">
      <div className="cardContainer">
        <TribeSelect challengeId={id} tribeData={cardState.challenge.Tribe} />
        <SelectAllChallenges
          challengeId={id}
          challengeData={cardState.challenge}
        />
        <SelectAllActualState
          challengeId={id}
          actualStateData={cardState.actualState}
        />
        <TargetSta challengeId={id} targetStateData={cardState.targetState} />
      </div>
    </div>
  );
};

export default Card;