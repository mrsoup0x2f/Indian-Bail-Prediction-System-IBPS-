import React from 'react';
import './TeamMembers.css';

const teamMembers = [
    {
        id: 1,
        name: 'Prof. Aranb Bhattacharya',
        role: 'Supervisor',
        imageUrl: '/arnab6.jpg',
        description: 'Professor, Department of Computer Science and Engineering, IIT Kanpur',
    },
    {
        id: 2,
        name: 'Shubham Kumar Nigam',
        role: 'Mentor',
        imageUrl: '/shubham.png',
        description: 'PhD@IIT Kanpur, DAAD Postdoc-NeT-AI Fellow',
    },
    {
        id: 3,
        name: 'Puspesh Kumar Srivastava',
        role: 'Team Member',
        imageUrl: '/puspesh.jpg',
        description: 'MSR,Department of Computer Science and Engineering, IIT Kanpur',
    },
    {
        id: 4,
        name: 'Praveen Patel',
        role: 'Team Member',
        imageUrl: '/praveen.jpeg',
        description: 'MSR,Department of Computer Science and Engineering, IIT Kanpur',
    },
    {
        id: 5,
        name: 'Uddeshya Raj',
        role: 'Team Member',
        imageUrl: '/uddeshya.png',
        description: 'MSR,Department of Computer Science and Engineering, IIT Kanpur',
    },
    {
        id: 6,
        name: 'Parjanya Aditya Shukla',
        role: 'Team Member',
        imageUrl: '/parjanya.jpg',
        description: 'MTech,Department of Computer Science and Engineering, IIT Kanpur',
    },
    // {
    //     id: 7,
    //     name: 'Noel Shallum',
    //     role: 'Team Member',
    //     imageUrl: '/noel.jpeg',
    //     description: 'BBA.LLB (Hons.), Law ,Symbiosis Law School, Pune',
    // },
];

const TeamMembers = () => {
    return (
        <div className="team-container">
            {teamMembers.map(member => (
                <div key={member.id} className="team-card">
                    <div className="team-image-wrapper">
                        <img src={member.imageUrl} alt={member.name} className="team-image" />
                    </div>
                    <h3 className="team-name">{member.name}</h3>
                    <p className="team-role">{member.role}</p>
                    <p className="team-description">{member.description}</p>
                </div>
            ))}
        </div>
    );
};

export default TeamMembers;
