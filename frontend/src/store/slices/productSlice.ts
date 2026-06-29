import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import {productApi} from '../../services/api';
import {ProductState} from '../../types';

const initialState: ProductState = {
  currentProduct: null,
  analysis: null,
  recommendations: [],
  isLoading: false,
  error: null,
};

export const scanBarcode = createAsyncThunk(
  'product/scan',
  async (barcode: string, {rejectWithValue}) => {
    try {
      const res = await productApi.scan(barcode);
      return res.data.product;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error ?? 'Scan failed');
    }
  },
);

export const analyzeProduct = createAsyncThunk(
  'product/analyze',
  async (barcode: string, {rejectWithValue}) => {
    try {
      const res = await productApi.analyze(barcode);
      return res.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error ?? 'Analysis failed');
    }
  },
);

export const fetchRecommendations = createAsyncThunk(
  'product/recommendations',
  async (category: string | undefined, {rejectWithValue}) => {
    try {
      const res = await productApi.recommendations(category);
      return res.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error ?? 'Failed to load recommendations');
    }
  },
);

const productSlice = createSlice({
  name: 'product',
  initialState,
  reducers: {
    clearProduct: state => {
      state.currentProduct = null;
      state.analysis = null;
    },
    clearError: state => {
      state.error = null;
    },
  },
  extraReducers: builder => {
    builder
      .addCase(scanBarcode.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(scanBarcode.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentProduct = action.payload;
      })
      .addCase(scanBarcode.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(analyzeProduct.pending, state => {
        state.isLoading = true;
      })
      .addCase(analyzeProduct.fulfilled, (state, action) => {
        state.isLoading = false;
        state.analysis = action.payload;
      })
      .addCase(analyzeProduct.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchRecommendations.fulfilled, (state, action) => {
        state.recommendations = action.payload;
      });
  },
});

export const {clearProduct, clearError} = productSlice.actions;
export default productSlice.reducer;
