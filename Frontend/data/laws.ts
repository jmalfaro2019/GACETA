// Mock data for Colombian Congress Oversight

export interface VotingStats {
  favor: number;
  against: number;
  abstentions: number;
  total: number;
}

export interface Law {
  id: string;
  title: string;
  description: string;
  filingDate: string;
  status: string;
  statusColor: string;
  author: string;
  party: string;
  partyColor: string;
  voting: {
    favor: number;
    against: number;
    abstentions: number;
  };
  chatHistory: any[];
}

const laws: Law[] = [
  {
    id: "pl-043-2024",
    title: "Bill 043 – Healthcare Reform",
    description: "Structural reform of the Colombian healthcare system. Eliminates EPS as intermediaries and transfers resources directly to public clinics and hospitals.",
    filingDate: "2024-03-15",
    status: "In Debate",
    statusColor: "amber",
    author: "Government / MinSalud",
    party: "Pacto Histórico",
    partyColor: "purple",
    voting: {
      favor: 45,
      against: 12,
      abstentions: 5,
    },
    chatHistory: [],
  },
];

export default laws;
