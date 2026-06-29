import React, {useEffect} from 'react';
import {View, StyleSheet, ScrollView, Image} from 'react-native';
import {Text, Surface, Chip, Button, ProgressBar, ActivityIndicator} from 'react-native-paper';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {RouteProp} from '@react-navigation/native';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {analyzeProduct} from '../store/slices/productSlice';
import {RootStackParamList, AnalysisResult} from '../types';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'ProductDetail'>;
  route: RouteProp<RootStackParamList, 'ProductDetail'>;
};

const PREDICTION_COLORS = {Safe: '#52b788', Caution: '#f4a261', Avoid: '#e63946'};
const NUTRISCORE_COLORS: Record<string, string> = {a: '#038141', b: '#85bb2f', c: '#fecb02', d: '#ee8100', e: '#e63312'};
const NOVA_LABELS: Record<number, string> = {1: 'Unprocessed', 2: 'Processed culinary', 3: 'Processed', 4: 'Ultra-processed'};

export default function ProductDetailScreen({navigation, route}: Props) {
  const dispatch = useAppDispatch();
  const {currentProduct: product, analysis, isLoading} = useAppSelector(s => s.product);
  const {barcode} = route.params;

  useEffect(() => {
    if (barcode && !analysis) {
      dispatch(analyzeProduct(barcode));
    }
  }, [barcode]);

  if (isLoading || !product) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
        <Text style={{marginTop: 12}}>Analyzing product...</Text>
      </View>
    );
  }

  const predictionColor = analysis ? PREDICTION_COLORS[analysis.prediction] : '#888';

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {product.image_url ? (
        <Image source={{uri: product.image_url}} style={styles.image} resizeMode="contain" />
      ) : (
        <View style={[styles.image, styles.imagePlaceholder]}>
          <Text style={styles.imagePlaceholderText}>🛒</Text>
        </View>
      )}

      <Text variant="headlineSmall" style={styles.productName}>{product.name}</Text>
      <Text variant="bodyMedium" style={styles.brand}>{product.brand || 'Unknown brand'}</Text>

      {/* Labels */}
      <View style={styles.row}>
        {product.is_vegan && <Chip icon="leaf" style={styles.vegChip}>Vegan</Chip>}
        {product.is_vegetarian && !product.is_vegan && <Chip icon="leaf" style={styles.vegChip}>Vegetarian</Chip>}
        {product.nutriscore_grade && (
          <Chip style={[styles.nutriChip, {backgroundColor: NUTRISCORE_COLORS[product.nutriscore_grade]}]}>
            Nutriscore {product.nutriscore_grade.toUpperCase()}
          </Chip>
        )}
        {product.nova_group && (
          <Chip style={styles.novaChip}>NOVA {product.nova_group}</Chip>
        )}
      </View>

      {/* AI Analysis */}
      {analysis && (
        <Surface style={styles.analysisCard} elevation={2}>
          <View style={[styles.predictionBadge, {backgroundColor: predictionColor}]}>
            <Text style={styles.predictionText}>{analysis.prediction}</Text>
            <Text style={styles.confidenceText}>{analysis.confidence}% confidence</Text>
          </View>

          {analysis.issues.length > 0 && (
            <View style={styles.issuesSection}>
              <Text variant="titleSmall" style={styles.sectionTitle}>⚠️ Health Concerns</Text>
              {analysis.issues.map((issue, idx) => (
                <Surface key={idx} style={styles.issueItem} elevation={1}>
                  <Text style={styles.issueIngredient}>{issue.ingredient}</Text>
                  <Text style={styles.issueReason}>{issue.reason}</Text>
                </Surface>
              ))}
            </View>
          )}
        </Surface>
      )}

      {/* Nutrition */}
      <Surface style={styles.nutritionCard} elevation={1}>
        <Text variant="titleSmall" style={styles.sectionTitle}>Nutrition per 100g</Text>
        {Object.entries(product.nutrition_per_100g).map(([key, value]) =>
          value != null ? (
            <View key={key} style={styles.nutritionRow}>
              <Text style={styles.nutritionKey}>{key.replace(/_/g, ' ')}</Text>
              <Text style={styles.nutritionValue}>{String(value)}</Text>
            </View>
          ) : null,
        )}
      </Surface>

      {/* Ingredients */}
      {product.ingredients_text && (
        <Surface style={styles.ingredientsCard} elevation={1}>
          <Text variant="titleSmall" style={styles.sectionTitle}>Ingredients</Text>
          <Text variant="bodySmall" style={styles.ingredientsText}>{product.ingredients_text}</Text>
        </Surface>
      )}

      <Button
        mode="contained"
        icon="chat"
        onPress={() => navigation.navigate('Chat', {barcode: product.barcode})}
        style={styles.chatButton}>
        Ask AI About This Product
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f5f5f5'},
  content: {padding: 16, paddingBottom: 32},
  centered: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  image: {width: '100%', height: 200, borderRadius: 12, marginBottom: 16},
  imagePlaceholder: {backgroundColor: '#e0e0e0', justifyContent: 'center', alignItems: 'center'},
  imagePlaceholderText: {fontSize: 64},
  productName: {fontWeight: '700', marginBottom: 4},
  brand: {color: '#666', marginBottom: 12},
  row: {flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16},
  vegChip: {backgroundColor: '#d8f3dc'},
  nutriChip: {borderRadius: 16},
  novaChip: {backgroundColor: '#e9ecef'},
  analysisCard: {borderRadius: 12, padding: 16, marginBottom: 16, backgroundColor: '#fff'},
  predictionBadge: {borderRadius: 10, padding: 16, alignItems: 'center', marginBottom: 12},
  predictionText: {color: '#fff', fontSize: 22, fontWeight: '800'},
  confidenceText: {color: '#fff', opacity: 0.9, marginTop: 2},
  issuesSection: {gap: 8},
  sectionTitle: {fontWeight: '700', marginBottom: 8},
  issueItem: {borderRadius: 8, padding: 12, backgroundColor: '#fff8f8'},
  issueIngredient: {fontWeight: '600', color: '#c62828'},
  issueReason: {color: '#555', marginTop: 2},
  nutritionCard: {borderRadius: 12, padding: 16, marginBottom: 16, backgroundColor: '#fff'},
  nutritionRow: {flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 4, borderBottomWidth: 1, borderBottomColor: '#f0f0f0'},
  nutritionKey: {color: '#555', textTransform: 'capitalize'},
  nutritionValue: {fontWeight: '600'},
  ingredientsCard: {borderRadius: 12, padding: 16, marginBottom: 16, backgroundColor: '#fff'},
  ingredientsText: {color: '#555', lineHeight: 20},
  chatButton: {borderRadius: 8, marginTop: 8},
});
