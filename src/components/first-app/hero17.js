import React, { Fragment } from 'react'
import { useNavigate } from 'react-router-dom';
import Script from 'dangerous-html/react'
import PropTypes from 'prop-types'

import './hero17.css'

const Hero17 = (props) => {

  const navigate = useNavigate();

  const handleStartPredicting = () => {
    navigate('/predict'); // This navigates to the PredictionPage
  };
  return (
    <div className="hero17-video-section">
      ̥ <video
        className="hero17-video-bg"
        src="/bg.mp4"
        autoPlay
        loop
        muted
        playsInline
      />
      <div className="hero17-video-overlay"></div>
      <div className="hero17-header78">
        <div className="hero17-column thq-section-padding thq-section-max-width">
          <div className="hero17-content1">
            <h1 className="hero17-text1 thq-heading-1">
              {props.heading1 ?? (
                <Fragment>
                  <span className="hero17-text7">
                    INDIAN BAIL PREDICTION SYSTEM
                  </span>
                </Fragment>
              )}
            </h1>
            <p className="hero17-text2 thq-body-large">
              {props.content1 ?? (
                <Fragment>
                  <span className="hero17-text8">
                    Welcome to the Indian Bail Prediction System. We provide accurate predictions and
                    insights into bail outcomes using advanced AI technology. Our
                    platform leverages data-driven algorithms to assist legal
                    professionals in making informed decisions.
                  </span>
                </Fragment>
              )}
            </p>
          </div>
          <div className="hero17-actions">
            <button className="thq-button-filled" type='button' onClick={handleStartPredicting} style={{ borderColor: 'white', backgroundColor: 'transparent', backgroundImage: 'None' }}>
              <span className="thq-body-small">
                {props.action1 ?? (
                  <Fragment>
                    <span className="hero17-text6">Try it out</span>
                  </Fragment>
                )}
              </span>
            </button>
            {/* <button className="thq-button-outline hero17-button2">
              <span className="thq-body-small">
                {props.action2 ?? (
                  <Fragment>
                    <span className="hero17-text5">Secondary action</span>
                  </Fragment>
                )}
              </span>
            </button> */}
          </div>
        </div>
        <div className="hero17-content2">
          <div className="hero17-row-container1 thq-animated-group-container-horizontal thq-mask-image-horizontal">
            <div className="thq-animated-group-horizontal">
              <img
                alt={props.image1Alt}
                src="/Mumbai_03-2016_41_Bombay_High_Court.jpg"
                className="hero17-placeholder-image10 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image2Alt}
                src="/छत्तीसगढ़_उच्च_न्यायालय_बिलासपुर.jpeg"
                className="hero17-placeholder-image11 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image3Alt}
                src="/High_Court_of_Kerala_Building.jpg"
                className="hero17-placeholder-image12 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image4Alt}
                src="/Allahabad_high_court.jpg"
                className="hero17-placeholder-image13 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image5Alt}
                src="/Supreme_Court_of_India_01.jpg"
                className="hero17-placeholder-image14 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image6Alt}
                src="/High_Court_of_Karnataka.jpg"
                className="hero17-placeholder-image15 thq-img-scale thq-img-ratio-1-1"
              />
            </div>
            <div className="thq-animated-group-horizontal">
              <img
                alt={props.image1Alt}
                src="/Jharkhand _high_court.jpg"
                className="hero17-placeholder-image16 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image2Alt}
                src="/orissa-high-court.jpg"
                className="hero17-placeholder-image17 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image3Alt}
                src="/Division-Bench-of-Jammu-Kashmir-and-Ladakh-High-Court.jpg"
                className="hero17-placeholder-image18 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image4Alt}
                src="/Rajashthan_High_Court.jpg"
                className="hero17-placeholder-image19 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt={props.image5Alt}
                src={props.image5Src}
                className="hero17-placeholder-image20 thq-img-scale thq-img-ratio-1-1"
              />
              <img
                alt="Hero Image"
                src="https://images.unsplash.com/photo-1534312527009-56c7016453e6?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDIxfHxhYnN0cmFjdHxlbnwwfHx8fDE3MTA4NzA5MzB8MA&amp;ixlib=rb-4.0.3&amp;w=1500"
                className="hero17-placeholder-image21 thq-img-scale thq-img-ratio-1-1"
              />
            </div>
          </div>
        </div>
        <div>
          <div className="hero17-container2">
            <Script
              html={`<style>
          @keyframes scroll-x {
            from {
              transform: translateX(0);
            }
            to {
              transform: translateX(calc(-100% - 16px));
            }
          }

          @keyframes scroll-y {
            from {
              transform: translateY(0);
            }
            to {
              transform: translateY(calc(-100% - 16px));
            }
          }
        </style>
        `}
            ></Script>
          </div>
        </div>
      </div>
    </div>
  )
}

Hero17.defaultProps = {
  image3Src:
    'https://images.unsplash.com/photo-1574169208507-84376144848b?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDN8fGFic3RyYWN0fGVufDB8fHx8MTcxMDg3MDkzMHww&ixlib=rb-4.0.3&w=1500',
  image8Alt: 'Hero Image',
  image2Src:
    'https://images.unsplash.com/photo-1552083974-186346191183?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDE1fHxhYnN0cmFjdHxlbnwwfHx8fDE3MTA4NzA5MzB8MA&ixlib=rb-4.0.3&w=1500',
  image6Alt: 'Hero Image',
  image11Src:
    'https://images.unsplash.com/photo-1524169358666-79f22534bc6e?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDI3fHxhYnN0cmFjdHxlbnwwfHx8fDE3MTA4NzA5MzB8MA&ixlib=rb-4.0.3&w=1500',
  image5Alt: 'Hero Image',
  image1Alt: 'Hero Image',
  image7Src:
    'https://images.unsplash.com/photo-1561212044-bac5ef688a07?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDIyfHxhYnN0cmFjdHxlbnwwfHx8fDE3MTA4NzA5MzB8MA&ixlib=rb-4.0.3&w=1500',
  image7Alt: 'Hero Image',
  image12Alt: 'Hero Image',
  image2Alt: 'Hero Image',
  image6Src:
    'https://images.unsplash.com/photo-1534312527009-56c7016453e6?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDIxfHxhYnN0cmFjdHxlbnwwfHx8fDE3MTA4NzA5MzB8MA&ixlib=rb-4.0.3&w=1500',
  image12Src:
    'https://images.unsplash.com/photo-1568214379698-8aeb8c6c6ac8?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDEyfHxncmFmaWN8ZW58MHx8fHwxNzE1Nzk0OTk5fDA&ixlib=rb-4.0.3&w=1500',
  image3Alt: 'Hero Image',
  image9Src:
    'https://images.unsplash.com/photo-1506259091721-347e791bab0f?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDExfHxhYnN0cmFjdHxlbnwwfHx8fDE3MTA4NzA5MzB8MA&ixlib=rb-4.0.3&w=1500',
  image11Alt: 'Hero Image',
  action2: undefined,
  action1: undefined,
  image8Src:
    'https://images.unsplash.com/photo-1557672172-298e090bd0f1?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDEwfHxhYnN0cmFjdHxlbnwwfHx8fDE3MTA4NzA5MzB8MA&ixlib=rb-4.0.3&w=1500',
  image5Src:
    'https://images.unsplash.com/photo-1604076913837-52ab5629fba9?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDh8fGFic3RyYWN0fGVufDB8fHx8MTcxMDg3MDkzMHww&ixlib=rb-4.0.3&w=1500',
  image4Src:
    'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDV8fGFic3RyYWN0fGVufDB8fHx8MTcxMDg3MDkzMHww&ixlib=rb-4.0.3&w=1500',
  image10Alt: 'Hero Image',
  image4Alt: 'Hero Image',
  heading1: undefined,
  content1: undefined,
  image10Src:
    'https://images.unsplash.com/photo-1553356084-58ef4a67b2a7?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDI0fHxhYnN0cmFjdHxlbnwwfHx8fDE3MTA4NzA5MzB8MA&ixlib=rb-4.0.3&w=1500',
  image9Alt: 'Hero Image',
  image1Src:
    'https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDJ8fGFic3RyYWN0fGVufDB8fHx8MTcxMDg3MDkzMHww&ixlib=rb-4.0.3&w=1500',
}

Hero17.propTypes = {
  image3Src: PropTypes.string,
  image8Alt: PropTypes.string,
  image2Src: PropTypes.string,
  image6Alt: PropTypes.string,
  image11Src: PropTypes.string,
  image5Alt: PropTypes.string,
  image1Alt: PropTypes.string,
  image7Src: PropTypes.string,
  image7Alt: PropTypes.string,
  image12Alt: PropTypes.string,
  image2Alt: PropTypes.string,
  image6Src: PropTypes.string,
  image12Src: PropTypes.string,
  image3Alt: PropTypes.string,
  image9Src: PropTypes.string,
  image11Alt: PropTypes.string,
  action2: PropTypes.element,
  action1: PropTypes.element,
  image8Src: PropTypes.string,
  image5Src: PropTypes.string,
  image4Src: PropTypes.string,
  image10Alt: PropTypes.string,
  image4Alt: PropTypes.string,
  heading1: PropTypes.element,
  content1: PropTypes.element,
  image10Src: PropTypes.string,
  image9Alt: PropTypes.string,
  image1Src: PropTypes.string,
}

export default Hero17
