import React, {useState, useCallback} from 'react';
import {View, StyleSheet, Alert, Vibration} from 'react-native';
import {Text, Button, TextInput, Surface} from 'react-native-paper';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {scanBarcode, analyzeProduct} from '../store/slices/productSlice';
import {RootStackParamList} from '../types';

type Props = {navigation: NativeStackNavigationProp<RootStackParamList, 'Scanner'>};

export default function ScannerScreen({navigation}: Props) {
  const dispatch = useAppDispatch();
  const {isLoading} = useAppSelector(s => s.product);
  const [manualBarcode, setManualBarcode] = useState('');
  const [scanned, setScanned] = useState(false);

  const handleBarcode = useCallback(
    async (barcode: string) => {
      if (!barcode.trim()) return;
      setScanned(true);
      Vibration.vibrate(100);

      try {
        const result = await dispatch(scanBarcode(barcode.trim())).unwrap();
        await dispatch(analyzeProduct(barcode.trim())).unwrap();
        navigation.navigate('ProductDetail', {barcode: barcode.trim()});
      } catch (err: any) {
        Alert.alert('Product Not Found', err ?? 'Could not find this product. Try entering the barcode manually.');
        setScanned(false);
      }
    },
    [dispatch, navigation],
  );

  const handleManualEntry = () => {
    if (!manualBarcode.trim()) {
      Alert.alert('Error', 'Please enter a barcode number.');
      return;
    }
    handleBarcode(manualBarcode.trim());
  };

  return (
    <View style={styles.container}>
      {/* Camera scanner would be mounted here via react-native-vision-camera */}
      <View style={styles.cameraPlaceholder}>
        <Text variant="bodyLarge" style={styles.cameraText}>
          📷 Point camera at barcode
        </Text>
        <View style={styles.scanFrame} />
        <Text variant="bodySmall" style={styles.hintText}>
          Hold steady over the barcode
        </Text>
      </View>

      <Surface style={styles.manualSection} elevation={2}>
        <Text variant="titleMedium" style={styles.manualTitle}>Or enter barcode manually</Text>
        <TextInput
          label="Barcode number"
          value={manualBarcode}
          onChangeText={setManualBarcode}
          keyboardType="numeric"
          left={<TextInput.Icon icon="barcode" />}
          style={styles.input}
        />
        <Button
          mode="contained"
          onPress={handleManualEntry}
          loading={isLoading}
          disabled={isLoading}
          style={styles.button}>
          Search Product
        </Button>

        <Button
          mode="outlined"
          onPress={() => navigation.navigate('Chat', {})}
          style={[styles.button, {marginTop: 8}]}>
          Ask AI Instead
        </Button>
      </Surface>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#000'},
  cameraPlaceholder: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#1a1a2e'},
  cameraText: {color: '#fff', marginBottom: 40},
  scanFrame: {
    width: 260,
    height: 160,
    borderWidth: 3,
    borderColor: '#52b788',
    borderRadius: 12,
    marginBottom: 20,
  },
  hintText: {color: '#aaa'},
  manualSection: {
    padding: 20,
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  manualTitle: {fontWeight: '700', marginBottom: 12},
  input: {marginBottom: 12},
  button: {borderRadius: 8},
});
