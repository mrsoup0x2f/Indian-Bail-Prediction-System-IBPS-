import React, { Fragment } from 'react'
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types'

import './cta26.css'

const CTA26 = (props) => {
  const navigate = useNavigate();

  const handleStartPredicting = () => {
    navigate('/predict'); // This navigates to the PredictionPage
  };

  return (
    <div className="thq-section-padding">
      <div className="thq-section-max-width">
        <div className="cta26-accent2-bg">
          <div className="cta26-accent1-bg">
            <div className="cta26-container2">
              <div className="cta26-content">
                <span className="thq-heading-2">
                  {props.heading1 ?? (
                    <Fragment>
                      <span className="cta26-text4">
                        Get Started with Bail Prediction
                      </span>
                    </Fragment>
                  )}
                </span>
                <p className="thq-body-large">
                  {props.content1 ?? (
                    <Fragment>
                      <span className="cta26-text5">
                        Prepare your documents and details — you're about to step into the courtroom with ease and speed.
                      </span>
                    </Fragment>
                  )}
                </p>
              </div>
              <div className="cta26-actions">
                <button
                  type="button"
                  className="thq-button-filled cta26-button"
                  onClick={handleStartPredicting} // Add this onClick handler
                >
                  <span>
                    {props.action1 ? (
                      <Fragment>
                        <span className="cta26-text">Start Predicting</span>
                      </Fragment>
                    ) : null}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

CTA26.defaultProps = {
  heading1: undefined,
  content1: undefined,
  action1: undefined,
}

CTA26.propTypes = {
  heading1: PropTypes.element,
  content1: PropTypes.element,
  action1: PropTypes.element,
}

export default CTA26
