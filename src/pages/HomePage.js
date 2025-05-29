import React, { Fragment } from 'react'

import { Helmet } from 'react-helmet'

import Navbar8 from '../components/first-app/navbar8'
import Hero17 from '../components/first-app/hero17'
import Features24 from '../components/first-app/features24'
import CTA26 from '../components/first-app/cta26'
import Features25 from '../components/first-app/features25'
import Steps2 from '../components/first-app/steps2'
import Testimonial17 from '../components/first-app/testimonial17'
import Contact10 from '../components/first-app/contact10'
import TeamMembers from '../components/first-app/TeamMembers'
import Footer4 from '../components/first-app/footer4'
import './home.css'

const Home = (props) => {
    return (

        <div className="home-container">
            <Helmet>
                <title>IBPS</title>
                <meta property="og:title" content="IBPS" />
            </Helmet>
            {/* <Navbar8
                page4Description={
                    <Fragment>
                        <span className="home-text100">Get in touch with us</span>
                    </Fragment>
                }
                action1={
                    <Fragment>
                        <span className="home-text101">Try it out</span>
                    </Fragment>
                }
                link2={
                    <Fragment>
                        <span className="home-text102">#about</span>
                    </Fragment>
                }
                page1={
                    <Fragment>
                        <span className="home-text103">Home</span>
                    </Fragment>
                }
                link1={
                    <Fragment>
                        <span className="home-text104">#home</span>
                    </Fragment>
                }
                page4={
                    <Fragment>
                        <span className="home-text105">Contact</span>
                    </Fragment>
                }
                page2={
                    <Fragment>
                        <span className="home-text106">About</span>
                    </Fragment>
                }
                link4={
                    <Fragment>
                        <span className="home-text107">#contact</span>
                    </Fragment>
                }
                page1Description={
                    <Fragment>
                        <span className="home-text108">Welcome to Bail Prediction</span>
                    </Fragment>
                }
                page2Description={
                    <Fragment>
                        <span className="home-text109">
                            Learn more about Bail Prediction
                        </span>
                    </Fragment>
                }
                link3={
                    <Fragment>
                        <span className="home-text110">#services</span>
                    </Fragment>
                }
                page3={
                    <Fragment>
                        <span className="home-text111">Services</span>
                    </Fragment>
                }
                page3Description={
                    <Fragment>
                        <span className="home-text112">Explore our legal services</span>
                    </Fragment>
                }
                action2={
                    <Fragment>
                        <span className="home-text113">Contact Us</span>
                    </Fragment>
                }
            ></Navbar8> */}
            <Hero17
                action1={
                    <Fragment>
                        <span className="home-text115">Try it out</span>
                    </Fragment>
                }
                heading1={
                    <Fragment>
                        <span className="home-text116">
                            INDIAN BAIL PREDICTION SYSTEM
                        </span>
                    </Fragment>
                }
                content1={
                    <Fragment>
                        <span className="home-text117">
                            Welcome to the Indian Bail Prediction System. We provide accurate predictions and
                            insights into bail outcomes using advanced AI technology. Our
                            platform leverages data-driven algorithms to assist legal
                            professionals in making informed decisions.
                        </span>
                    </Fragment>
                }
            ></Hero17>
            <Features24
                feature3Description={
                    <Fragment>
                        <span className="home-text118">Courts take 23–156 days to decide bail — justice delayed, lives disrupted.</span>
                    </Fragment>
                }
                feature3Title={
                    <Fragment>
                        <span className="home-text119">Justice Delayed</span>
                    </Fragment>
                }
                feature2Description={
                    <Fragment>
                        <span className="home-text120">
                            Overcrowded prisons harm lives, public health, and justice..
                        </span>
                    </Fragment>
                }
                feature1Title={
                    <Fragment>
                        <span className="home-text121"> 75.8% Are Undertrials</span>
                    </Fragment>
                }
                feature1Description={
                    <Fragment>
                        <span className="home-text122">
                            Most prisoners are awaiting trial — mainly from poor, marginalized groups. (NCRB 2021–22)
                        </span>
                    </Fragment>
                }
                feature2Title={
                    <Fragment>
                        <span className="home-text123"> Jails Overstuffed (131%)</span>
                    </Fragment>
                }
            ></Features24>
            <Features25
                feature3Description={
                    <Fragment>
                        <span className="home-text127">
                            Our training data consists of a diverse range of legal cases, ensuring comprehensive coverage of various scenarios.It includes datasets from the Supreme Court and High Courts across India.
                        </span>
                    </Fragment>
                }
                feature1Description={
                    <Fragment>
                        <span className="home-text128">
                            Uses Phi-4 and CNN to predict bail outcomes from High Court data with lightning speed and accuracy.</span>
                    </Fragment>
                }
                feature2Title={
                    <Fragment>
                        <span className="home-text129">Interactive Chatbot</span>
                    </Fragment>
                }
                feature1Title={
                    <Fragment>
                        <span className="home-text130">Advanced AI Algorithms</span>
                    </Fragment>
                }
                feature2Description={
                    <Fragment>
                        <span className="home-text131">
                            Interact with our AI tool in a user-friendly chatbot interface with real-time responses.
                        </span>
                    </Fragment>
                }
                feature3Title={
                    <Fragment>
                        <span className="home-text132">Big Data Corpus</span>
                    </Fragment>
                }
            ></Features25>

            <Steps2
                step1Description={
                    <Fragment>
                        <span className="home-text184">
                            AI will need your case information like the incident details, past criminal records, age and health details, possible arguments for or against your case and the date of arrest in case of regular bail applications.
                        </span>
                    </Fragment>
                }
                step3Description={
                    <Fragment>
                        <span className="home-text185">
                            Get instant predictions on the likelihood of bail being granted for your case along with graphical confidence score.
                        </span>
                    </Fragment>
                }
                step2Title={
                    <Fragment>
                        <span className="home-text186">AI Prediction</span>
                    </Fragment>
                }
                step2Description={
                    <Fragment>
                        <span className="home-text187">
                            Our advanced AI tool uses Large Language Models (LLMs) and CNN to process your request and predict bail outcomes based on historical case data.
                        </span>
                    </Fragment>
                }
                step1Title={
                    <Fragment>
                        <span className="home-text188">Explain your case</span>
                    </Fragment>
                }
                step3Title={
                    <Fragment>
                        <span className="home-text189">Receive Prediction</span>
                    </Fragment>
                }
                step4Description={
                    <Fragment>
                        <span className="home-text190">
                            Use the predictions to make informed decisions and strategize legal proceedings effectively. Good luck!
                        </span>
                    </Fragment>
                }
                step4Title={
                    <Fragment>
                        <span className="home-text191">Make Informed Decisions</span>
                    </Fragment>
                }
            ></Steps2>
            <CTA26
                heading1={
                    <Fragment>
                        <span className="home-text124">
                            Get Started with Bail Prediction
                        </span>
                    </Fragment>
                }
                content1={
                    <Fragment>
                        <span className="home-text125">
                            Prepare your documents and details — you're about to step into the courtroom with ease and speed.
                        </span>
                    </Fragment>
                }
                action1={
                    <Fragment>
                        <span className="home-text126">Start Predicting</span>
                    </Fragment>
                }
            ></CTA26>
            <Testimonial17
                author2Position={
                    <Fragment>
                        <span className="home-text192"></span>
                    </Fragment>
                }
                author1Position={
                    <Fragment>
                        <span className="home-text193">Lawyer</span>
                    </Fragment>
                }
                author1Name={
                    <Fragment>
                        <span className="home-text194">Multilingual Support</span>
                    </Fragment>
                }
                author3Name={
                    <Fragment>
                        <span className="home-text195">Multiple Document & File Type Support</span>
                    </Fragment>
                }
                review2={
                    <Fragment>
                        <span className="home-text196">
                            Interact hands-free with our tool using intuitive voice commands for faster and more accessible bail predictions.
                        </span>
                    </Fragment>
                }
                author2Name={
                    <Fragment>
                        <span className="home-text197">Voice Enabled Support</span>
                    </Fragment>
                }
                author4Position={
                    <Fragment>
                        <span className="home-text198">Law Student</span>
                    </Fragment>
                }
                author4Name={
                    <Fragment>
                        <span className="home-text199">Dataset Expansion</span>
                    </Fragment>
                }
                content1={
                    <Fragment>
                        <span className="home-text200">
                            We are learners we don't stop exploring new ideas and
                            possibilities.
                        </span>
                    </Fragment>
                }
                author3Position={
                    <Fragment>
                        <span className="home-text201">Judge</span>
                    </Fragment>
                }
                review1={
                    <Fragment>
                        <span className="home-text202">
                            We are going to add more Indian languages like Hindi, Marathi, Bengali,Tamil to our platform to make it
                            accessible to a wider audience. Stay tuned for updates!
                        </span>
                    </Fragment>
                }
                heading1={
                    <Fragment>
                        <span className="home-text203">Upcoming Features!</span>
                    </Fragment>
                }
                review3={
                    <Fragment>
                        <span className="home-text204">
                            Seamlessly upload and analyze multiple documents, including images and PDFs, all in one go.
                        </span>
                    </Fragment>
                }
                review4={
                    <Fragment>
                        <span className="home-text205">
                            Enhanced prediction accuracy powered by a richer, more diverse dataset trained on broader legal scenarios
                        </span>
                    </Fragment>
                }
            ></Testimonial17>

            {/* New added code for team section */}
            <div className="home-team-section">
                <h2 className="home-team-heading">Our Team</h2>
                <p className="home-team-description">Meet the experts behind the Indian Bail Prediction System</p>
                <TeamMembers />
            </div>
            <Contact10
                content1={
                    <Fragment>
                        <span className="home-text206">
                            Have a question or need assistance? Feel free to reach out to us.
                        </span>
                    </Fragment>
                }
                location1Description={
                    <Fragment>
                        <span className="home-text207">
                            Visit our office during business hours.
                        </span>
                    </Fragment>
                }
                heading1={
                    <Fragment>
                        <span className="home-text208">Contact Us</span>
                    </Fragment>
                }
                location2Description={
                    <Fragment>
                        <span className="home-text209">Send us an email anytime.</span>
                    </Fragment>
                }
                location1={
                    <Fragment>
                        <span className="home-text210">
                            Department of Computer Science and Engineering, IIT Kanpur, India.
                        </span>
                    </Fragment>
                }
                location2={
                    <Fragment>
                        <span className="home-text211">Our Dedicated team Members</span>
                    </Fragment>
                }
            ></Contact10>
            <Footer4
                link5={
                    <Fragment>
                        <span className="home-text212">Privacy Policy</span>
                    </Fragment>
                }
                link3={
                    <Fragment>
                        <span className="home-text213">FAQs</span>
                    </Fragment>
                }
                link1={
                    <Fragment>
                        <span className="home-text214">About Us</span>
                    </Fragment>
                }
                termsLink={
                    <Fragment>
                        <span className="home-text215"></span>
                    </Fragment>
                }
                link2={
                    <Fragment>
                        <span className="home-text216">Contact Us</span>
                    </Fragment>
                }
                link4={
                    <Fragment>
                        <span className="home-text217"></span>
                    </Fragment>
                }
                cookiesLink={
                    <Fragment>
                        <span className="home-text218"></span>
                    </Fragment>
                }
                privacyLink={
                    <Fragment>
                        <span className="home-text219"></span>
                    </Fragment>
                }
            ></Footer4>
        </div>
    )
}

export default Home
