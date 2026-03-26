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
  status: string;
  statusColor: string;
  author: string;
  party: string;
  partyColor: string;
  filingDate: string;
  voting: VotingStats;
  chatHistory: { role: "user" | "ai"; text: string }[];
}

const laws: Law[] = [
  {
    id: "pl-043-2024",
    title: "Bill 043 – Healthcare Reform",
    description:
      "Structural reform of the Colombian healthcare system. Eliminates EPS as intermediaries and transfers resources directly to public clinics and hospitals.",
    status: "In second debate",
    statusColor: "amber",
    author: "Sen. Francia Márquez Mina",
    party: "Historic Pact",
    partyColor: "purple",
    filingDate: "2024-03-10",
    voting: { favor: 54, against: 47, abstentions: 8, total: 109 },
    chatHistory: [
      {
        role: "user",
        text: "What does eliminating the EPS mean in practice?",
      },
      {
        role: "ai",
        text:
          "If the EPS is eliminated, healthcare system resources would go directly to hospitals and clinics. This aims to reduce financial intermediation, but some experts warn of transition risks due to state operational capacity.",
      },
      {
        role: "user",
        text: "When would it take effect if approved?",
      },
      {
        role: "ai",
        text:
          "According to the current text, implementation would be gradual: 18 months for urban areas and 24 months for rural and remote areas from the law's enactment.",
      },
    ],
  },
  {
    id: "pl-127-2024",
    title: "Bill 127 – Extended Paternity Leave",
    description:
      "Extends paternity leave from 2 weeks to 8 weeks paid, progressively equalizing it with maternity leave to promote shared responsibility at home.",
    status: "Approved",
    statusColor: "green",
    author: "Sen. Ariel Ávila Martínez",
    party: "Colombia Humana",
    partyColor: "red",
    filingDate: "2024-01-22",
    voting: { favor: 89, against: 12, abstentions: 5, total: 106 },
    chatHistory: [
      {
        role: "user",
        text: "Who benefits from this law?",
      },
      {
        role: "ai",
        text:
          "All working fathers with formal employment contracts in Colombia. The law applies to both private and public sectors and also covers same-sex couples.",
      },
    ],
  },
  {
    id: "pl-208-2024",
    title: "Bill 208 – Life Sentence for Femicide",
    description:
      "Proposes amending the Penal Code to establish a reviewable life sentence (minimum 25 years) for persons convicted of aggravated femicide.",
    status: "In first debate",
    statusColor: "blue",
    author: "Sen. Paloma Valencia Laserna",
    party: "Democratic Center",
    partyColor: "orange",
    filingDate: "2024-05-08",
    voting: { favor: 61, against: 39, abstentions: 12, total: 112 },
    chatHistory: [
      {
        role: "user",
        text: "Is life imprisonment constitutional in Colombia?",
      },
      {
        role: "ai",
        text:
          "It's an active debate. In 2021, Congress approved a legislative act allowing life sentences for rapists and child murderers, but the Constitutional Court declared it unconstitutional. This new proposal attempts different language to overcome that ruling.",
      },
      {
        role: "user",
        text: "How many votes does it need to advance to second debate?",
      },
      {
        role: "ai",
        text:
          "It requires a simple majority (half plus one of members present) in the Senate's first committee to advance to second debate in plenary.",
      },
    ],
  },
  {
    id: "pl-315-2024",
    title: "Bill 315 – Internet as a Fundamental Right",
    description:
      "Declares internet access a fundamental right, requires the State to guarantee free basic connectivity in rural areas, and creates the National Digital Inclusion Fund.",
    status: "Archived",
    statusColor: "gray",
    author: "Rep. David Racero Mayorca",
    party: "Historic Pact",
    partyColor: "purple",
    filingDate: "2023-11-14",
    voting: { favor: 38, against: 62, abstentions: 9, total: 109 },
    chatHistory: [
      {
        role: "user",
        text: "Why was this bill archived?",
      },
      {
        role: "ai",
        text:
          "The bill was archived at the end of the legislative term without being debated in plenary. According to Congress rules, bills that don't advance in two consecutive legislatures are automatically archived.",
      },
    ],
  },
];

export default laws;
