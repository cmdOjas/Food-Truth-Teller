import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import {profileApi} from '../../services/api';
import {ProfileState, UserProfile} from '../../types';

const initialState: ProfileState = {
  profile: null,
  isLoading: false,
  error: null,
};

export const fetchProfile = createAsyncThunk('profile/fetch', async (_, {rejectWithValue}) => {
  try {
    const res = await profileApi.get();
    return res.data as UserProfile;
  } catch (err: any) {
    if (err.response?.status === 404) return null;
    return rejectWithValue(err.response?.data?.error ?? 'Failed to load profile');
  }
});

export const saveProfile = createAsyncThunk(
  'profile/save',
  async (data: Partial<UserProfile>, {rejectWithValue}) => {
    try {
      const res = await profileApi.save(data as Record<string, unknown>);
      return res.data.profile as UserProfile;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error ?? 'Failed to save profile');
    }
  },
);

const profileSlice = createSlice({
  name: 'profile',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null;
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchProfile.pending, state => {
        state.isLoading = true;
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.profile = action.payload;
      })
      .addCase(fetchProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(saveProfile.pending, state => {
        state.isLoading = true;
      })
      .addCase(saveProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.profile = action.payload;
      })
      .addCase(saveProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const {clearError} = profileSlice.actions;
export default profileSlice.reducer;
