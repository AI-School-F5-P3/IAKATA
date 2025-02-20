import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  getChallenge,
  validateChallengePassword,
} from "../../services/challengeServices";
import SearchBar from "../../components/searchBar/SearchBar";
import Calendar from "react-calendar";
import "./Home.css";
import "../../components/calendar/Calendar";
import { getActualState } from "../../services/actualStateServices";
import PasswordModal from "../../components/passwordModal/PasswordModal";
import Swal from "sweetalert2";
import { useWebSocket } from "../../context/SocketContext";

const Home = () => {
  const [challenges, setChallenges] = useState([]);
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [filteredChallenges, setFilteredChallenges] = useState([]);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const navigate = useNavigate();
  const calendarRef = useRef(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [selectedChallengeId, setSelectedChallengeId] = useState(null);
  const { socket, isConnected, WS_EVENTS } = useWebSocket();
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 7;

  const handleChallengeClick = (challenge) => {
    setSelectedChallengeId(challenge.id);
    setShowPasswordModal(true);
  };

  const handlePasswordSubmit = async (password) => {
    try {
        const response = await validateChallengePassword(selectedChallengeId, password);
        if (response.isValid) {
            navigate(`/home/card/${selectedChallengeId}`);
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Contraseña incorrecta',
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
    } catch (error) {
        console.error("Error:", error);
    }
    setShowPasswordModal(false);
};

  const filterByDate = (challenges, date) => {
    if (!date) return challenges;
    const selectedDateTime = new Date(date);
    return challenges.filter((challenge) => {
      const challengeDate = new Date(challenge.start_date);
      return challengeDate.toDateString() === selectedDateTime.toDateString();
    });
  };

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [challengesData, actualStatesData] = await Promise.all([
        getChallenge(),
        getActualState(),
      ]);

      const challengesWithData = challengesData.map((challenge) => ({
        ...challenge,
        actual_state:
          actualStatesData.find((state) => state.challenge_id === challenge.id)?.description || "Sin descripción",
      }));
      setChallenges(challengesWithData);
      setFilteredChallenges(challengesWithData);
    } catch (error) {
      console.error("Error al cargar datos:", error);
      setError("Error al cargar los datos");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!socket || !isConnected) return;

    const handleWebSocketMessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        if (
          data.type === WS_EVENTS.CHALLENGE ||
          data.type === WS_EVENTS.ACTUAL_STATE
        ) {
          await fetchData();
        }
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };

    socket.addEventListener("message", handleWebSocketMessage);
    return () => {
      socket.removeEventListener("message", handleWebSocketMessage);
    };
  }, [socket, isConnected]);

  useEffect(() => {
    fetchData();
  }, []);

  const handleDateChange = (date) => {
    setSelectedDate(date);
    setFilteredChallenges(filterByDate(challenges, date));
  };

  const toggleCalendar = () => {
    setIsCalendarOpen(!isCalendarOpen);
  };

  const handleOutsideClick = (event) => {
    if (calendarRef.current && !calendarRef.current.contains(event.target)) {
      setIsCalendarOpen(false);
    }
  };

  const handleSearch = (searchTerm) => {
    const filteredResults = challenges.filter((challenge) => {
      return Object.values(challenge).some(
        (value) =>
          typeof value === "string" &&
          value.toLowerCase().includes(searchTerm.toLowerCase())
      );
    });
    setFilteredChallenges(filteredResults);
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, []);

  const indexLastItem = currentPage * itemsPerPage;
  const indexFirstItem = indexLastItem - itemsPerPage;
  const currentItems = filteredChallenges.slice(indexFirstItem, indexLastItem);
  const totalPages = Math.ceil(filteredChallenges.length / itemsPerPage); 

   return (
    <div className="home-container">
      <div className="container-principal">
        <SearchBar onSearch={handleSearch} />
        <button onClick={toggleCalendar} className="button-calendar">
          Calendario
        </button>
        {isCalendarOpen && (
          <div ref={calendarRef} className="calendar-wrapper">
            <Calendar onChange={handleDateChange} value={selectedDate} />
          </div>
        )}
      </div>
      <div className="table-container">
        <table className="responsive-table">
          <thead className="thead-home">
            <tr className="title-tr-home">
              <th className="title-th-home">RETO</th>
              <th className="title-th-home">NOMBRE</th>
              <th className="title-th-home">ESTADO ACTUAL</th>
            </tr>
          </thead>
          <tbody>
            {currentItems.map((challenge) => (
              <tr
                className="table-challenge"
                key={challenge.id}
                onClick={() => handleChallengeClick(challenge)}
              >
                <td className="challenge-wrapper idWrapper">{challenge.id}</td>
                <td className="challenge-wrapper">{challenge.name}</td>
                <td className="challenge-wrapper">{challenge.actual_state}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className='pagination'>
          <button className="bton-pagination" onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} disabled={currentPage === 1}>Anterior</button>
          <span>Página {currentPage} de {totalPages}</span>
          <button className="bton-pagination" onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))} disabled={currentPage === totalPages}>Siguiente</button>
       </div> 
      {showPasswordModal && (
        <PasswordModal
          onSubmit={handlePasswordSubmit}
          onClose={() => setShowPasswordModal(false)}
        />
      )}
    </div>
    
  );
};

export default Home;