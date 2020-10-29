import { LOGOUT, LOGIN } from "../actionTypes";

const initialState = {
    userName: "",
};

export default function(state = initialState, action) {
    switch (action.type) {
      case LOGIN: {
        const { userName } = action.data;
        return {
          ...state,
          userName,
        };
      }
      case LOGOUT: {
        return {
          ...state,
          userName: "",
        };
      }
      default:
        return state;
    }
}