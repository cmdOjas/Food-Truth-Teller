import React, {useEffect} from 'react';
import {View, StyleSheet, ScrollView} from 'react-native';
import {Text, Surface, Button, Chip} from 'react-native-paper';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {fetchProfile} from '../store/slices/profileSlice';
import {fetchRecommendations} from '../store/slices/productSlice';
import {RootStackParamList} from '../types';

type Props = {navigation: NativeStackNavigationProp<RootStackParamList, 'Main'>};

export default function HomeScreen({navigation}: Props) {
  const dispatch = useAppDispatch();
  const {user} = useAppSelector(s => s.auth);
  const {profile} = useAppSelector(s => s.profile);
  const {recommendations} = useAppSelector(s => s.product);

  useEffect(() => {
    dispatch(fetchProfile());
    dispatch(fetchRecommendations(undefined));
  }, []);

  const bmi = profile?.bmi;
  const bmiLabel = !bmi ? null : bmi < 18.5 ? 'Underweight' : bmi < 25 ? 'Normal' : bmi < 30 ? 'Overweight' : 'Obese';

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.greeting}>
        Hello, {user?.name?.split(' ')[0] ?? 'User'} 👋
      </Text>
      <Text variant="bodyMedium" style={styles.subtitle}>
        Scan food barcodes to check if they're safe for you
      </Text>

      {/* Quick Actions */}
      <View style={styles.actions}>
        <Surface style={styles.actionCard} elevation={2} onTouchEnd={() => navigation.navigate('Scanner')}>
          <Text style={styles.actionIcon}>📷</Text>
          <Text variant="titleSmall" style={styles.actionLabel}>Scan Barcode</Text>
        </Surface>
        <Surface style={styles.actionCard} elevation={2} onTouchEnd={() => navigation.navigate('Chat', {})}>
          <Text style={styles.actionIcon}>🤖</Text>
          <Text variant="titleSmall" style={styles.actionLabel}>Ask AI</Text>
        </Surface>
        <Surface style={styles.actionCard} elevation={2} onTouchEnd={() => navigation.navigate('Profile')}>
          <Text style={styles.actionIcon}>👤</Text>
          <Text variant="titleSmall" style={styles.actionLabel}>My Profile</Text>
        </Surface>
        <Surface style={styles.actionCard} elevation={2} onTouchEnd={() => navigation.navigate('History')}>
          <Text style={styles.actionIcon}>💬</Text>
          <Text variant="titleSmall" style={styles.actionLabel}>History</Text>
        </Surface>
      </View>

      {/* Health Summary */}
      {profile && (
        <Surface style={styles.healthCard} elevation={1}>
          <Text variant="titleMedium" style={styles.cardTitle}>Your Health Profile</Text>
          <View style={styles.healthRow}>
            {profile.health_conditions?.length > 0 && (
              <View style={styles.healthItem}>
                <Text variant="bodySmall" style={styles.healthLabel}>Conditions</Text>
                <View style={styles.chips}>
                  {profile.health_conditions.slice(0, 3).map(c => (
                    <Chip key={c} compact style={styles.chip}>{c}</Chip>
                  ))}
                </View>
              </View>
            )}
            {profile.allergies?.length > 0 && (
              <View style={styles.healthItem}>
                <Text variant="bodySmall" style={styles.healthLabel}>Allergies</Text>
                <View style={styles.chips}>
                  {profile.allergies.slice(0, 3).map(a => (
                    <Chip key={a} compact style={[styles.chip, styles.allergyChip]}>{a}</Chip>
                  ))}
                </View>
              </View>
            )}
          </View>
          {bmi && (
            <Text variant="bodySmall" style={styles.bmi}>BMI: {bmi} ({bmiLabel})</Text>
          )}
          {!profile.age && (
            <Button mode="outlined" onPress={() => navigation.navigate('Profile')} style={styles.setupBtn}>
              Complete your profile for better results
            </Button>
          )}
        </Surface>
      )}

      {/* Healthy Recommendations */}
      {recommendations.length > 0 && (
        <Surface style={styles.recoCard} elevation={1}>
          <Text variant="titleMedium" style={styles.cardTitle}>Healthy Picks 🌿</Text>
          {recommendations.slice(0, 4).map(p => (
            <Surface
              key={p.id}
              style={styles.recoItem}
              elevation={0}
              onTouchEnd={() => navigation.navigate('ProductDetail', {barcode: p.barcode})}>
              <Text variant="bodyMedium" style={styles.recoName} numberOfLines={1}>{p.name}</Text>
              <Text variant="bodySmall" style={styles.recoBrand}>{p.brand}</Text>
              {p.nutriscore_grade && (
                <Text variant="bodySmall" style={styles.recoScore}>
                  Nutriscore {p.nutriscore_grade.toUpperCase()}
                </Text>
              )}
            </Surface>
          ))}
        </Surface>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f5f5f5'},
  content: {padding: 20, paddingBottom: 40},
  greeting: {fontWeight: '800', color: '#2d6a4f'},
  subtitle: {color: '#666', marginTop: 4, marginBottom: 24},
  actions: {flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 20},
  actionCard: {
    width: '46%',
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
  },
  actionIcon: {fontSize: 36, marginBottom: 8},
  actionLabel: {fontWeight: '600', textAlign: 'center'},
  healthCard: {borderRadius: 16, padding: 16, backgroundColor: '#fff', marginBottom: 20},
  cardTitle: {fontWeight: '700', marginBottom: 12},
  healthRow: {gap: 12},
  healthItem: {marginBottom: 8},
  healthLabel: {color: '#888', marginBottom: 6},
  chips: {flexDirection: 'row', flexWrap: 'wrap', gap: 6},
  chip: {backgroundColor: '#e8f5e9'},
  allergyChip: {backgroundColor: '#fce4e4'},
  bmi: {color: '#666', marginTop: 8},
  setupBtn: {marginTop: 12},
  recoCard: {borderRadius: 16, padding: 16, backgroundColor: '#fff'},
  recoItem: {
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f9f9f9',
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#52b788',
  },
  recoName: {fontWeight: '600'},
  recoBrand: {color: '#888', marginTop: 2},
  recoScore: {color: '#2d6a4f', marginTop: 2},
});
