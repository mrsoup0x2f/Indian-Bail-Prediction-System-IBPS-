import React from 'react'
import ReactDOM from 'react-dom'
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect,
} from 'react-router-dom'

import './style.css'
import App from './App'

// const App = () => {
//   return (
//     <Router>
//       <Switch>
//         <Route component={Home} exact path="/" />
//         <Route component={NotFound} path="**" />
//         <Redirect to="**" />
//       </Switch>
//     </Router>
//   )
// }


ReactDOM.render(<App />, document.getElementById('root'))
