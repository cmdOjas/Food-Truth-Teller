import React, {useState, useEffect} from 'react';
import {View, StyleSheet, ScrollView, Alert} from 'react-native';
import {Text, TextInput, Button, Surface, Chip, SegmentedButtons, ActivityIndicator} from 'react-native-paper';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {fetchProfile, saveProfile} from '../store/slices/profileSlice';
import {UserProfile} from '../types';

const HEALTH_CONDITIONS = ['Diabetes', 'Hypertension', 'Celiac Disease', 'Cardiovascular Disease', 'Obesity', 'Kidney Disease', 'Thyroid', 'Liver Disease'];
const ALLERGENS = ['Gluten', 'Dairy', 'Nuts', 'Soy', 'Eggs', 'Fish', 'Shellfish', 'Peanuts'];
const DIET_OPTIONS = [
  {value: 'none', label: 'None'},
  {value: 'vegetarian', label: 'Vegetarian'},
  {value: 'vegan', label: 'Vegan'},
  {value: 'keto', label: 'Keto'},
  {value: 'gluten-free', label: 'Gluten-Free'},
];
const GOALS = ['Lose Weight', 'Gain Muscle', 'Lower Cholesterol', 'Manage Diabetes', 'Heart Health', 'General Wellness'];

export default function ProfileScreen() {
  const dispatch = useAppDispatch();
  const {profile, isLoading} = useAppSelector(s => s.profile);

  const [age, setAge] = useState('');
  const [gender, setGender] = useState<'male' | 'female' | 'other'>('male');
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
  const [selectedAllergens, setSelectedAllergens] = useState<string[]>([]);
  const [diet, setDiet] = useState('none');
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  useEffect(() => {
    dispatch(fetchProfile());
  }, []);

  useEffect(() => {
    if (profile) {
      setAge(String(profile.age ?? ''));
      setGender((profile.gender as 'male' | 'female' | 'other') ?? 'male');
      setWeight(String(profile.weight_kg ?? ''));
      setHeight(String(profile.height_cm ?? ''));
      setSelectedConditions(profile.health_conditions ?? []);
      setSelectedAllergens(profile.allergies ?? []);
      setDiet(profile.diet_preference ?? 'none');
      setSelectedGoals(profile.goals ?? []);
    }
  }, [profile]);

  const toggleItem = (arr: string[], item: string, setter: (v: string[]) => void) => {
    setter(arr.includes(item) ? arr.filter(i => i !== item) : [...arr, item]);
  };

  const handleSave = async () => {
    const data: Partial<UserProfile> = {
      age: age ? parseInt(age, 10) : undefined,
      gender,
      weight_kg: weight ? parseFloat(weight) : undefined,
      height_cm: height ? parseFloat(height) : undefined,
      health_conditions: selectedConditions,
      allergies: selectedAllergens.map(a => a.toLowerCase()),
      diet_preference: diet,
      goals: selectedGoals,
    };
    try {
      await dispatch(saveProfile(data)).unwrap();
      Alert.alert('Success', 'Profile saved successfully!');
    } catch (err: any) {
      Alert.alert('Error', err ?? 'Failed to save profile.');
    }
  };

  if (isLoading && !profile) {
    return <View style={styles.centered}><ActivityIndicator size="large" /></View>;
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineSmall" style={styles.heading}>My Health Profile</Text>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Basic Information</Text>
        <TextInput label="Age" value={age} onChangeText={setAge} keyboardType="numeric" style={styles.input} />
        <SegmentedButtons
          value={gender}
          onValueChange={v => setGender(v as 'male' | 'female' | 'other')}
          buttons={[{value: 'male', label: 'Male'}, {value: 'female', label: 'Female'}, {value: 'other', label: 'Other'}]}
          style={styles.segmented}
        />
        <TextInput label="Weight (kg)" value={weight} onChangeText={setWeight} keyboardType="decimal-pad" style={styles.input} />
        <TextInput label="Height (cm)" value={height} onChangeText={setHeight} keyboardType="decimal-pad" style={styles.input} />
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Health Conditions</Text>
        <View style={styles.chips}>
          {HEALTH_CONDITIONS.map(c => (
            <Chip
              key={c}
              selected={selectedConditions.includes(c)}
              onPress={() => toggleItem(selectedConditions, c, setSelectedConditions)}
              style={styles.chip}>
              {c}
            </Chip>
          ))}
        </View>
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Allergies</Text>
        <View style={styles.chips}>
          {ALLERGENS.map(a => (
            <Chip
              key={a}
              selected={selectedAllergens.includes(a)}
              onPress={() => toggleItem(selectedAllergens, a, setSelectedAllergens)}
              style={styles.chip}>
              {a}
            </Chip>
          ))}
        </View>
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Diet Preference</Text>
        <View style={styles.chips}>
          {DIET_OPTIONS.map(d => (
            <Chip
              key={d.value}
              selected={diet === d.value}
              onPress={() => setDiet(d.value)}
              style={styles.chip}>
              {d.label}
            </Chip>
          ))}
        </View>
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Health Goals</Text>
        <View style={styles.chips}>
          {GOALS.map(g => (
            <Chip
              key={g}
              selected={selectedGoals.includes(g)}
              onPress={() => toggleItem(selectedGoals, g, setSelectedGoals)}
              style={styles.chip}>
              {g}
            </Chip>
          ))}
        </View>
      </Surface>

      <Button mode="contained" onPress={handleSave} loading={isLoading} disabled={isLoading} style={styles.saveButton} contentStyle={styles.saveButtonContent}>
        Save Profile
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f5f5f5'},
  content: {padding: 16, paddingBottom: 32},
  centered: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  heading: {fontWeight: '700', marginBottom: 16, color: '#2d6a4f'},
  section: {borderRadius: 12, padding: 16, marginBottom: 16, backgroundColor: '#fff'},
  sectionTitle: {fontWeight: '700', marginBottom: 12},
  input: {marginBottom: 12},
  segmented: {marginBottom: 12},
  chips: {flexDirection: 'row', flexWrap: 'wrap', gap: 8},
  chip: {marginBottom: 4},
  saveButton: {borderRadius: 8, marginTop: 8},
  saveButtonContent: {paddingVertical: 6},
});
